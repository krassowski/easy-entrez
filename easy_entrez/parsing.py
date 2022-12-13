"""Additional parsing utilities, require pandas to be installed."""
import re
from dataclasses import dataclass
from warnings import warn
from xml.dom import minidom
from xml.etree import ElementTree

from .api import EntrezResponse, is_xml_response, is_response_for
from .queries import FetchQuery

try:
    from pandas import DataFrame
except ImportError:
    DataFrame = None


namespaces = {'ns0': 'https://www.ncbi.nlm.nih.gov/SNP/docsum'}


def xml_to_string(element):
    return (
        minidom.parseString(ElementTree.tostring(element))
        .toprettyxml(indent=' ' * 4)
    )


@dataclass
class VariantSet:
    coordinates: DataFrame
    alt_frequencies: DataFrame


def parse_dbsnp_variants(snps_result: EntrezResponse, verbose: bool = False) -> VariantSet:
    if DataFrame is None:
        raise ValueError('pandas is required for parser_dbsnp_variants')
    if not is_xml_response(snps_result):
        raise ValueError('Can only parse an XML response')
    if not is_response_for(snps_result, FetchQuery):
        raise ValueError('Expected FetchQuery response')
    snps = snps_result.data

    results = []
    alt_frequencies = []

    for i, snp in enumerate(snps):
        error = snp.find('.//ns0:error', namespaces)
        if error is not None:
            warn(f'Failed to retrieve {snps_result.query.ids[i]} due to error: {error.text}')
            continue
        rs_id = snp.find('.//ns0:SNP_ID', namespaces).text
        spdi_text = snp.find('.//ns0:SPDI', namespaces).text
        if not spdi_text:
            warn(f'Failed to retrieve {snps_result.query.ids[i]}: SPDI not found')
            if verbose:
                print(xml_to_string(snp))
            continue
        spdi = spdi_text.split(',')
        chrom, pos = snp.find('.//ns0:CHRPOS', namespaces).text.split(':')
        chrom_prev, pos_prev = snp.find('.//ns0:CHRPOS_PREV_ASSM', namespaces).text.split(':')
        sig_class = snp.find('.//ns0:FXN_CLASS', namespaces).text

        expected_ref = {
            s.split(':')[-2]
            for s in spdi
        }
        assert len(expected_ref) == 1

        expected_alt = [
            s.split(':')[-1]
            for s in spdi
        ]

        for maf in snp.findall('.//ns0:GLOBAL_MAFS/ns0:MAF', namespaces):
            studies = maf.findall('.//ns0:STUDY', namespaces)
            assert len(studies) == 1
            study = list(studies)[0].text
            for frequency in maf.findall('.//ns0:FREQ', namespaces):
                match_obj = re.match(
                    r'(?P<alt>(?:A|C|T|G|-)+)=(?P<frequency>\d+.\d*)/(?P<count>\d+)',
                    frequency.text
                )
                if not match_obj:
                    warn(f'Unrecognised variant FREQ format: {frequency.text} for rs{rs_id}')
                    continue
                match = match_obj.groupdict()
                freq = float(match['frequency'])
                if freq > 1:
                    warn(f'frequency {freq} > 1 for variant: rs{rs_id}')
                    continue
                alt_frequencies.append({
                    'rs_id': f'rs{rs_id}',
                    'allele': match['alt'],
                    'source_frequency': freq,
                    'total_count': int(match['count']),
                    'study': study,
                    'count': freq * int(match['count']),
                })

        results.append({
            'rs_id': f'rs{rs_id}',
            'ref': list(expected_ref)[0],
            'alts': ','.join(expected_alt),
            'chrom': chrom,
            'pos': float(pos),
            'chrom_prev': chrom_prev,
            'pos_prev': float(pos_prev),
            'consequence': sig_class
        })

    return VariantSet(
        coordinates=DataFrame(results).set_index('rs_id'),
        alt_frequencies=DataFrame(alt_frequencies)
    )

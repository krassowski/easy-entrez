"""Additional parsing utilities, require pandas to be installed."""
import re
from dataclasses import dataclass
from warnings import warn
from xml.dom import minidom
from xml.etree import ElementTree
from typing import Union, Dict

from .api import EntrezResponse, is_xml_response, is_response_for
from .queries import FetchQuery

try:
    from pandas import DataFrame, concat
except ImportError:
    DataFrame = None


namespaces = {'ns0': 'https://www.ncbi.nlm.nih.gov/SNP/docsum'}


def xml_to_string(element, indent=' ' * 4):
    """Convert provided XML element to pretty indented string.

    Parameters:
        element: the XML element to convert (`data` attribute of entrez result)
        indent: the indentation to use, 4 spaces by default
    """
    return (
        minidom.parseString(ElementTree.tostring(element))
        .toprettyxml(indent=indent)
    )


@dataclass
class VariantSet:
    """Result of parsing with `parse_dbsnp_variants()`."""
    #: Coordinates of the SNPs in the genome and consequence (e.g. intro_variant).
    coordinates: DataFrame
    #: Frequencies of the alternative alleles.
    alt_frequencies: DataFrame
    #: Preferred identifiers map (old → new); old != new for merged variants.
    preferred_ids: dict
    #: Data from DOCSUM field including GENE, HGVS, etc.
    summary: DataFrame

    def __repr__(self):
        return f'<VariantSet with {len(self.coordinates)} variants>'


def parse_docsum(docsum: str) -> dict:
    result = {}
    for entry in docsum.split('|'):
        key, value = entry.split('=', maxsplit=1)
        result[key] = value
    if 'HGVS' in result:
        result['HGVS'] = result['HGVS'].replace('&gt;', '>').split(',')
    if 'LEN' in result:
        result['LEN'] = float(result['LEN'])
    return result


def parse_dbsnp_variants(snps_result: Union[EntrezResponse, Dict[tuple, EntrezResponse]], verbose: bool = False) -> VariantSet:
    """Parse coordinates, frequencies and preferred IDs of dbSNP variants.

    Parameters:
        snps_result: result of fetch query in XML format, usually to `'snp'` database
        verbose: whether to print out full problematic XML if SPDI cannot be parsed
    """
    if isinstance(snps_result, dict):
        coordinates = []
        alt_frequencies = []
        preferred_ids = {}
        summaries = []
        for result in snps_result.values():
            parsed = parse_dbsnp_variants(result)
            coordinates.append(parsed.coordinates)
            alt_frequencies.append(parsed.alt_frequencies)
            preferred_ids.update(parsed.preferred_ids)
            summaries.append(parsed.alt_frequencies)
        return VariantSet(
            coordinates=concat(coordinates),
            alt_frequencies=concat(alt_frequencies),
            preferred_ids=preferred_ids,
            summary=concat(summaries)
        )

    if DataFrame is None:
        raise ValueError('pandas is required for parser_dbsnp_variants')
    if not is_xml_response(snps_result):
        raise ValueError('Can only parse an XML response')
    if not is_response_for(snps_result, FetchQuery):
        raise ValueError('Expected FetchQuery response')
    snps = snps_result.data

    results = []
    alt_frequencies = []
    preferred_id = {}
    summaries = []

    for i, snp in enumerate(snps):
        error = snp.find('.//ns0:error', namespaces)
        if error is not None:
            warn(f'Failed to retrieve {snps_result.query.ids[i]} due to error: {error.text}')
            continue
        rs_id = snp.attrib['uid']
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

        doc_sum = snp.find('.//ns0:DOCSUM', namespaces).text
        try:
            doc_sum = parse_docsum(doc_sum)
            summaries.append({
                **doc_sum,
                'rs_id': f'rs{rs_id}'
            })
        except Exception as e:
            warn(f'Failed to parse DOCSUM: {e}')

        merged_into = snp.find('.//ns0:SNP_ID', namespaces).text
        if rs_id != merged_into:
            was_merged = snp.find('.//ns0:MERGED_SORT', namespaces).text
            assert was_merged == '1'

        preferred_id[f'rs{rs_id}'] = f'rs{merged_into}'

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
            'pos': int(pos),
            'chrom_prev': chrom_prev,
            'pos_prev': int(pos_prev),
            'consequence': sig_class
        })

    return VariantSet(
        coordinates=DataFrame(results).set_index('rs_id'),
        alt_frequencies=DataFrame(alt_frequencies),
        preferred_ids=preferred_id,
        summary=DataFrame(summaries).set_index('rs_id')
    )


__all__ = ['VariantSet', 'parse_dbsnp_variants', 'xml_to_string', 'namespaces']

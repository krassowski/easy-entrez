import pytest
from typing import Dict, Union
from dataclasses import dataclass
from xml.etree.ElementTree import Element, fromstring
from easy_entrez.parsing import parse_dbsnp_variants, VariantSet, parse_docsum
from easy_entrez.queries import FetchQuery
try:
    from typing import Literal
except ImportError:
    # python <=3.7
    Literal = Union

@dataclass
class DummyResponse:
    query: FetchQuery
    content_type: Literal['json', 'xml']
    data: Union[Element, Dict]


DOCSUM_CODING = "HGVS=NC_000012.12:g.21178699A&gt;G,NC_000012.11:g.21331633A&gt;G,NG_011745.1:g.52506A&gt;G,NM_006446.5:c.605A&gt;G,NM_006446.4:c.605A&gt;G,NP_006437.3:p.Glu202Gly|SEQ=[A/G]|LEN=1|GENE=SLCO1B1:10599"


def test_docsum():
    assert parse_docsum(DOCSUM_CODING) == {
        'HGVS': [
            'NC_000012.12:g.21178699A>G',
            'NC_000012.11:g.21331633A>G',
            'NG_011745.1:g.52506A>G',
            'NM_006446.5:c.605A>G',
            'NM_006446.4:c.605A>G',
            'NP_006437.3:p.Glu202Gly'
        ],
        'SEQ': '[A/G]',
        'LEN': 1,
        'GENE': 'SLCO1B1:10599'
    }


@pytest.mark.optional
def test_parse_two_snps():
    response = DummyResponse(
        query=FetchQuery(ids=['rs6311', 'rs662138'], database='snp', max_results=10),
        content_type='xml',
        data=fromstring(TWO_SNPS)
    )
    variant_set = parse_dbsnp_variants(response)
    assert type(variant_set) == VariantSet
    assert repr(variant_set) == '<VariantSet with 2 variants>'

    coordinates = variant_set.coordinates
    assert len(coordinates) == 2
    assert set(coordinates.index) == {'rs6311', 'rs662138'}
    rs6311 = coordinates.loc['rs6311']
    # GRCh38
    assert rs6311.pos == 46897343
    assert rs6311.chrom == '13'
    # GRCh37
    assert rs6311.pos_prev == 47471478
    assert rs6311.chrom_prev == '13'
    rs662138 = coordinates.loc['rs662138']
    assert rs662138.pos == 160143444
    assert rs662138.chrom == '6'

    frequencies = variant_set.alt_frequencies
    assert len(frequencies) == 41
    assert set(frequencies.rs_id) == {'rs6311', 'rs662138'}
    assert frequencies.source_frequency.min() > 0
    assert frequencies.source_frequency.max() < 1
    assert frequencies.total_count.min() > 0
    assert '1000Genomes' in set(frequencies.study)

    summary = variant_set.summary
    assert len(summary) == 2
    assert set(summary.index) == {'rs6311', 'rs662138'}
    assert set(summary.columns) == {'HGVS', 'SEQ', 'LEN', 'GENE'}


@pytest.mark.optional
def test_parse_batch():
    response = DummyResponse(
        query=FetchQuery(ids=['rs6311', 'rs662138'], database='snp', max_results=10),
        content_type='xml',
        data=fromstring(TWO_SNPS)
    )
    variant_set = parse_dbsnp_variants({('rs6311', 'rs662138'): response})
    assert type(variant_set) == VariantSet


@pytest.mark.optional
def test_merged_variant_solving():
    response = DummyResponse(
        query=FetchQuery(ids=['rs59679468'], database='snp', max_results=10),
        content_type='xml',
        data=fromstring(SNP_MERGED_INTO_ANOTHER)
    )
    variant_set = parse_dbsnp_variants(response)
    assert variant_set.preferred_ids == {'rs59679468': 'rs384162'}


TWO_SNPS = """\
<?xml version="1.0" ?>
<ns0:ExchangeSet xmlns:ns0="https://www.ncbi.nlm.nih.gov/SNP/docsum" xmlns:ns1="https://www.w3.org/2001/XMLSchema-instance" ns1:schemaLocation="https://www.ncbi.nlm.nih.gov/SNP/docsum ftp://ftp.ncbi.nlm.nih.gov/snp/specs/docsum_eutils.xsd">
    <ns0:DocumentSummary uid="6311">
        <ns0:SNP_ID>6311</ns0:SNP_ID>
        <ns0:ALLELE_ORIGIN/>
        <ns0:GLOBAL_MAFS>
            <ns0:MAF>
                <ns0:STUDY>1000Genomes</ns0:STUDY>
                <ns0:FREQ>T=0.44349/2221</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>ALSPAC</ns0:STUDY>
                <ns0:FREQ>T=0.411261/1585</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>Estonian</ns0:STUDY>
                <ns0:FREQ>T=0.331696/1486</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>GENOME_DK</ns0:STUDY>
                <ns0:FREQ>T=0.35/14</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>GnomAD</ns0:STUDY>
                <ns0:FREQ>T=0.402529/56309</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>GoNL</ns0:STUDY>
                <ns0:FREQ>T=0.400802/400</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>HGDP_Stanford</ns0:STUDY>
                <ns0:FREQ>T=0.408349/851</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>HapMap</ns0:STUDY>
                <ns0:FREQ>T=0.431746/816</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>KOREAN</ns0:STUDY>
                <ns0:FREQ>T=0.49727/1457</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>NorthernSweden</ns0:STUDY>
                <ns0:FREQ>T=0.323333/194</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>PAGE_STUDY</ns0:STUDY>
                <ns0:FREQ>T=0.416518/32775</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>PRJEB36033</ns0:STUDY>
                <ns0:FREQ>C=0.382979/36</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>PRJEB37584</ns0:STUDY>
                <ns0:FREQ>C=0.468274/369</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>Qatari</ns0:STUDY>
                <ns0:FREQ>C=0.49537/107</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>SGDP_PRJ</ns0:STUDY>
                <ns0:FREQ>C=0.368812/149</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>Siberian</ns0:STUDY>
                <ns0:FREQ>C=0.433333/13</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>TOMMO</ns0:STUDY>
                <ns0:FREQ>C=0.487053/8163</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>TOPMED</ns0:STUDY>
                <ns0:FREQ>T=0.407919/107972</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>TWINSUK</ns0:STUDY>
                <ns0:FREQ>T=0.405609/1504</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>Vietnamese</ns0:STUDY>
                <ns0:FREQ>C=0.247619/52</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>ALFA</ns0:STUDY>
                <ns0:FREQ>T=0.417763/70668</ns0:FREQ>
            </ns0:MAF>
        </ns0:GLOBAL_MAFS>
        <ns0:GLOBAL_POPULATION/>
        <ns0:GLOBAL_SAMPLESIZE>0</ns0:GLOBAL_SAMPLESIZE>
        <ns0:SUSPECTED/>
        <ns0:CLINICAL_SIGNIFICANCE>likely-benign</ns0:CLINICAL_SIGNIFICANCE>
        <ns0:GENES>
            <ns0:GENE_E>
                <ns0:NAME>HTR2A</ns0:NAME>
                <ns0:GENE_ID>3356</ns0:GENE_ID>
            </ns0:GENE_E>
        </ns0:GENES>
        <ns0:ACC>NC_000013.11</ns0:ACC>
        <ns0:CHR>13</ns0:CHR>
        <ns0:HANDLE>AFFY,BCM_SSAHASNP,SYSTEMSBIOZJU,GNOMAD,SC_SNP,TSC-CSHL,TOMMO_GENOMICS,EVA_SVP,SSMP,SGDP_PRJ,WEILL_CORNELL_DGM,EVA_UK10K_ALSPAC,URBANLAB,USC_VALOUEV,STEJUSTINE-REGGEN,ENSEMBL,PACBIO,ILLUMINA,GMI,EVA_UK10K_TWINSUK,COMPLETE_GENOMICS,BIOINF_KMB_FNS_UNIBA,KHV_HUMAN_GENOMES,KRGDB,BUSHMAN,GENOMED,PAGE_CC,HAMMER_LAB,JJLAB,EVA,CSHL-HAPMAP,1000GENOMES,HUMANGENOME_JCVI,EGCUT_WGS,EVA_DECODE,JMKIDD_LAB,EVA_GENOME_DK,SC_JCM,WIAF-CSNP,PERLEGEN,KRIBB_YJKIM,PJP,SSAHASNP,HGDP,BL,GRF,ACPOP,BGI,SWEGEN,CSHL,DDI,HUMAN_LONGEVITY,TISHKOFF,TOPMED,EVA-GONL</ns0:HANDLE>
        <ns0:SPDI>NC_000013.11:46897342:C:A,NC_000013.11:46897342:C:T</ns0:SPDI>
        <ns0:FXN_CLASS>upstream_transcript_variant,intron_variant,genic_upstream_transcript_variant</ns0:FXN_CLASS>
        <ns0:VALIDATED>by-frequency,by-alfa,by-cluster</ns0:VALIDATED>
        <ns0:DOCSUM>HGVS=NC_000013.11:g.46897343C&gt;A,NC_000013.11:g.46897343C&gt;T,NC_000013.10:g.47471478C&gt;A,NC_000013.10:g.47471478C&gt;T,NG_013011.1:g.4692G&gt;T,NG_013011.1:g.4692G&gt;A|SEQ=[C/A/T]|LEN=1|GENE=HTR2A:3356</ns0:DOCSUM>
        <ns0:TAX_ID>9606</ns0:TAX_ID>
        <ns0:ORIG_BUILD>52</ns0:ORIG_BUILD>
        <ns0:UPD_BUILD>155</ns0:UPD_BUILD>
        <ns0:CREATEDATE>2000/09/19 17:02</ns0:CREATEDATE>
        <ns0:UPDATEDATE>2021/04/26 09:46</ns0:UPDATEDATE>
        <ns0:SS>7939,2099948,5784016,11056913,13329238,17498388,19278078,21115889,23991391,51853939,67449420,67800891,68249902,70861814,71449210,75784706,83347152,97156264,103118544,112759807,132226882,154356844,159533108,160770133,168060669,171132048,173992917,199176358,211400969,226173755,236243610,242742025,254991385,281705525,291436716,481230318,481253884,482240219,485410505,537344692,563654829,659257781,778566866,783150704,784106672,832409896,833044346,834023844,990366795,1079068022,1348131587,1427181439,1576773719,1630233283,1673227316,1684889657,1713389819,1752106224,1807600745,1933735295,1959500160,1967777566,2027626970,2094795217,2095045201,2155992846,2196140100,2360268752,2628303786,2633061828,2700372086,2919384882,2985003440,2985639048,3010982218,3021506826,3027630728,3192080710,3350444661,3627061184,3631065273,3633049601,3633751914,3634544212,3635442009,3636231092,3637193085,3638010406,3639018180,3639819113,3640251542,3641041163,3641336058,3643000181,3643870142,3650028422,3651894390,3651894391,3653774270,3678245943,3695244544,3725392883,3739726578,3744844908,3751436465,3771745494,3772343978,3787451857,3792518952,3797402754,3816766312,3833534714,3840348211,3845833868,3847478318,3879928365,3928777472,3984680114,3985638434,4017632273,4945468980,5209892089</ns0:SS>
        <ns0:ALLELE>H</ns0:ALLELE>
        <ns0:SNP_CLASS>snv</ns0:SNP_CLASS>
        <ns0:CHRPOS>13:46897343</ns0:CHRPOS>
        <ns0:CHRPOS_PREV_ASSM>13:47471478</ns0:CHRPOS_PREV_ASSM>
        <ns0:TEXT/>
        <ns0:SNP_ID_SORT>0000006311</ns0:SNP_ID_SORT>
        <ns0:CLINICAL_SORT>1</ns0:CLINICAL_SORT>
        <ns0:CITED_SORT/>
        <ns0:CHRPOS_SORT>0046897343</ns0:CHRPOS_SORT>
        <ns0:MERGED_SORT>0</ns0:MERGED_SORT>
    </ns0:DocumentSummary>
    

    <ns0:DocumentSummary uid="662138">
        <ns0:SNP_ID>662138</ns0:SNP_ID>
        <ns0:ALLELE_ORIGIN/>
        <ns0:GLOBAL_MAFS>
            <ns0:MAF>
                <ns0:STUDY>1000Genomes</ns0:STUDY>
                <ns0:FREQ>G=0.118411/593</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>ALSPAC</ns0:STUDY>
                <ns0:FREQ>G=0.193046/744</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>Estonian</ns0:STUDY>
                <ns0:FREQ>G=0.154464/692</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>GENOME_DK</ns0:STUDY>
                <ns0:FREQ>G=0.225/9</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>GnomAD</ns0:STUDY>
                <ns0:FREQ>G=0.138558/19420</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>GoNL</ns0:STUDY>
                <ns0:FREQ>G=0.162325/162</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>HapMap</ns0:STUDY>
                <ns0:FREQ>G=0.117647/192</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>KOREAN</ns0:STUDY>
                <ns0:FREQ>G=0.001027/3</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>MGP</ns0:STUDY>
                <ns0:FREQ>G=0.136704/73</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>NorthernSweden</ns0:STUDY>
                <ns0:FREQ>G=0.155/93</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>PAGE_STUDY</ns0:STUDY>
                <ns0:FREQ>G=0.117242/9226</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>PRJEB36033</ns0:STUDY>
                <ns0:FREQ>G=0.088889/8</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>PRJEB37584</ns0:STUDY>
                <ns0:FREQ>G=0.002525/2</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>PRJEB37766</ns0:STUDY>
                <ns0:FREQ>G=0.291363/958</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>Qatari</ns0:STUDY>
                <ns0:FREQ>G=0.097222/21</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>SGDP_PRJ</ns0:STUDY>
                <ns0:FREQ>C=0.47541/58</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>Siberian</ns0:STUDY>
                <ns0:FREQ>C=0.444444/8</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>TOPMED</ns0:STUDY>
                <ns0:FREQ>G=0.141025/37328</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>TWINSUK</ns0:STUDY>
                <ns0:FREQ>G=0.171521/636</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>ALFA</ns0:STUDY>
                <ns0:FREQ>G=0.160454/13541</ns0:FREQ>
            </ns0:MAF>
        </ns0:GLOBAL_MAFS>
        <ns0:GLOBAL_POPULATION/>
        <ns0:GLOBAL_SAMPLESIZE>0</ns0:GLOBAL_SAMPLESIZE>
        <ns0:SUSPECTED/>
        <ns0:CLINICAL_SIGNIFICANCE/>
        <ns0:GENES>
            <ns0:GENE_E>
                <ns0:NAME>SLC22A1</ns0:NAME>
                <ns0:GENE_ID>6580</ns0:GENE_ID>
            </ns0:GENE_E>
        </ns0:GENES>
        <ns0:ACC>NC_000006.12</ns0:ACC>
        <ns0:CHR>6</ns0:CHR>
        <ns0:HANDLE>SGDP_PRJ,SSMP,SC_JCM,EVA_UK10K_TWINSUK,PERLEGEN,EVA_SVP,SI_EXO,EGCUT_WGS,AFFY,EVA_DECODE,ENSEMBL,1000GENOMES,KWOK,ABI,FSA-LAB,EVA_MGP,SWEGEN,TOPMED,WEILL_CORNELL_DGM,EVA,ILLUMINA,COMPLETE_GENOMICS,KRIBB_YJKIM,GRF,USC_VALOUEV,HUMAN_LONGEVITY,BIOINF_KMB_FNS_UNIBA,HAMMER_LAB,KHV_HUMAN_GENOMES,JMKIDD_LAB,JJLAB,CSHL-HAPMAP,BCMHGSC_JDW,PAGE_CC,GMI,BCM_SSAHASNP,ACPOP,KRGDB,GNOMAD,CSHL,EVA_GENOME_DK,EVA-GONL,TISHKOFF,GENOMED,EVA_UK10K_ALSPAC</ns0:HANDLE>
        <ns0:SPDI>NC_000006.12:160143443:C:G</ns0:SPDI>
        <ns0:FXN_CLASS>intron_variant</ns0:FXN_CLASS>
        <ns0:VALIDATED>by-frequency,by-alfa,by-cluster</ns0:VALIDATED>
        <ns0:DOCSUM>HGVS=NC_000006.12:g.160143444C&gt;G,NC_000006.11:g.160564476C&gt;G|SEQ=[C/G]|LEN=1|GENE=SLC22A1:6580</ns0:DOCSUM>
        <ns0:TAX_ID>9606</ns0:TAX_ID>
        <ns0:ORIG_BUILD>83</ns0:ORIG_BUILD>
        <ns0:UPD_BUILD>155</ns0:UPD_BUILD>
        <ns0:CREATEDATE>2000/08/11 14:20</ns0:CREATEDATE>
        <ns0:UPDATEDATE>2021/04/26 11:04</ns0:UPDATEDATE>
        <ns0:SS>835338,959497,1035197,1035759,2051156,10340406,24508718,44732279,68371153,68998600,76746537,76887987,93593714,104823350,111217410,144404952,162963366,222794264,233767468,285540024,410858957,559667618,654010923,983728334,1074206279,1323142041,1581983847,1593305004,1617166610,1660160643,1711148805,1712916761,1804770792,1926970596,1946197167,1958968850,1970575644,2024151598,2152344632,2290196722,2458886011,2634539291,2634539292,2635165219,2707983326,2711097223,2847573857,2986020641,3000296892,3022687346,3025866686,3347328367,3517507765,3625917861,3644930307,3653213070,3668237063,3718705650,3726403168,3734174646,3744282087,3744563611,3765937827,3771337836,3809100481,3838636043,3844086157,3866169000,3913159523,3984354004,3984354005,3984448642,3984580208,3985266167,3986365874,4729251304,5237411306</ns0:SS>
        <ns0:ALLELE>S</ns0:ALLELE>
        <ns0:SNP_CLASS>snv</ns0:SNP_CLASS>
        <ns0:CHRPOS>6:160143444</ns0:CHRPOS>
        <ns0:CHRPOS_PREV_ASSM>6:160564476</ns0:CHRPOS_PREV_ASSM>
        <ns0:TEXT/>
        <ns0:SNP_ID_SORT>0000662138</ns0:SNP_ID_SORT>
        <ns0:CLINICAL_SORT>0</ns0:CLINICAL_SORT>
        <ns0:CITED_SORT/>
        <ns0:CHRPOS_SORT>0160143444</ns0:CHRPOS_SORT>
        <ns0:MERGED_SORT>0</ns0:MERGED_SORT>
    </ns0:DocumentSummary>
    

</ns0:ExchangeSet>\
"""


SNP_MERGED_INTO_ANOTHER = """\
<?xml version="1.0" ?>
<ns0:ExchangeSet xmlns:ns0="https://www.ncbi.nlm.nih.gov/SNP/docsum" xmlns:ns1="https://www.w3.org/2001/XMLSchema-instance" ns1:schemaLocation="https://www.ncbi.nlm.nih.gov/SNP/docsum ftp://ftp.ncbi.nlm.nih.gov/snp/specs/docsum_eutils.xsd">
    <ns0:DocumentSummary uid="59679468">
        <ns0:SNP_ID>384162</ns0:SNP_ID>
        <ns0:ALLELE_ORIGIN/>
        <ns0:GLOBAL_MAFS>
            <ns0:MAF>
                <ns0:STUDY>1000Genomes</ns0:STUDY>
                <ns0:FREQ>T=0.474241/2375</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>ALSPAC</ns0:STUDY>
                <ns0:FREQ>A=0.370005/1426</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>Estonian</ns0:STUDY>
                <ns0:FREQ>A=0.34361/1538</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>GENOME_DK</ns0:STUDY>
                <ns0:FREQ>A=0.4/16</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>GnomAD</ns0:STUDY>
                <ns0:FREQ>A=0.4578/62552</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>GoNL</ns0:STUDY>
                <ns0:FREQ>A=0.373747/373</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>KOREAN</ns0:STUDY>
                <ns0:FREQ>T=0.321843/943</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>Korea1K</ns0:STUDY>
                <ns0:FREQ>T=0.33679/617</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>NorthernSweden</ns0:STUDY>
                <ns0:FREQ>A=0.334448/200</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>Qatari</ns0:STUDY>
                <ns0:FREQ>A=0.486111/105</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>SGDP_PRJ</ns0:STUDY>
                <ns0:FREQ>T=0.329949/130</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>Siberian</ns0:STUDY>
                <ns0:FREQ>T=0.386364/17</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>TOMMO</ns0:STUDY>
                <ns0:FREQ>T=0.316842/5309</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>TOPMED</ns0:STUDY>
                <ns0:FREQ>A=0.463674/122730</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>TWINSUK</ns0:STUDY>
                <ns0:FREQ>A=0.366775/1360</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>Vietnamese</ns0:STUDY>
                <ns0:FREQ>T=0.373832/80</ns0:FREQ>
            </ns0:MAF>
            <ns0:MAF>
                <ns0:STUDY>ALFA</ns0:STUDY>
                <ns0:FREQ>A=0.411416/7770</ns0:FREQ>
            </ns0:MAF>
        </ns0:GLOBAL_MAFS>
        <ns0:GLOBAL_POPULATION/>
        <ns0:GLOBAL_SAMPLESIZE>0</ns0:GLOBAL_SAMPLESIZE>
        <ns0:SUSPECTED/>
        <ns0:CLINICAL_SIGNIFICANCE/>
        <ns0:GENES>
            <ns0:GENE_E>
                <ns0:NAME>HRH1</ns0:NAME>
                <ns0:GENE_ID>3269</ns0:GENE_ID>
            </ns0:GENE_E>
        </ns0:GENES>
        <ns0:ACC>NC_000003.12</ns0:ACC>
        <ns0:CHR>3</ns0:CHR>
        <ns0:HANDLE>SGDP_PRJ,HAMMER_LAB,HGSV,EVA,SSAHASNP,ABI,GMI,1000GENOMES,ENSEMBL,URBANLAB,CSHL,TOMMO_GENOMICS,TOPMED,EGCUT_WGS,KHV_HUMAN_GENOMES,SWEGEN,EVA_UK10K_TWINSUK,USC_VALOUEV,COMPLETE_GENOMICS,PACBIO,JMKIDD_LAB,DDI,BL,EVA-GONL,WEILL_CORNELL_DGM,TISHKOFF,BUSHMAN,ACPOP,SYSTEMSBIOZJU,PJP,KRGDB,KOGIC,ILLUMINA-UK,GNOMAD,SC_JCM,EVA_UK10K_ALSPAC,JJLAB,HUMANGENOME_JCVI,BIOINF_KMB_FNS_UNIBA,HUMAN_LONGEVITY,EVA_GENOME_DK,GRF</ns0:HANDLE>
        <ns0:SPDI>NC_000003.12:11184947:T:A,NC_000003.12:11184947:T:C</ns0:SPDI>
        <ns0:FXN_CLASS>genic_upstream_transcript_variant,intron_variant</ns0:FXN_CLASS>
        <ns0:VALIDATED>by-frequency,by-alfa,by-cluster</ns0:VALIDATED>
        <ns0:DOCSUM>HGVS=NC_000003.12:g.11184948T&gt;A,NC_000003.12:g.11184948T&gt;C,NC_000003.11:g.11226634T&gt;A,NC_000003.11:g.11226634T&gt;C|SEQ=[T/A/C]|LEN=1|GENE=HRH1:3269</ns0:DOCSUM>
        <ns0:TAX_ID>9606</ns0:TAX_ID>
        <ns0:ORIG_BUILD>80</ns0:ORIG_BUILD>
        <ns0:UPD_BUILD>155</ns0:UPD_BUILD>
        <ns0:CREATEDATE>2000/07/17 02:10</ns0:CREATEDATE>
        <ns0:UPDATEDATE>2021/04/26 20:13</ns0:UPDATEDATE>
        <ns0:SS>494427,22007241,41928907,83601436,83901515,85646656,95984861,111255023,116974946,139358603,155104290,161921076,163109037,166160828,202135241,211136555,219980311,231707814,239141898,252932334,277013520,284595140,292932197,556425615,978271163,1070174768,1302799835,1429330472,1579844971,1606412769,1649406802,1798856369,1921523523,2021314871,2149382467,2249069294,2416110173,2625157295,2704742373,2789521091,2991828316,3024420373,3344884813,3382643285,3647340317,3659728467,3729631508,3759660202,3784234518,3789763204,3794636941,3802810406,3827661336,3855224541,3900996612,3950663555,4554179367,5157793592</ns0:SS>
        <ns0:ALLELE>H</ns0:ALLELE>
        <ns0:SNP_CLASS>snv</ns0:SNP_CLASS>
        <ns0:CHRPOS>3:11184948</ns0:CHRPOS>
        <ns0:CHRPOS_PREV_ASSM>3:11226634</ns0:CHRPOS_PREV_ASSM>
        <ns0:TEXT>MergedRs=384162</ns0:TEXT>
        <ns0:SNP_ID_SORT>0000384162</ns0:SNP_ID_SORT>
        <ns0:CLINICAL_SORT>0</ns0:CLINICAL_SORT>
        <ns0:CITED_SORT/>
        <ns0:CHRPOS_SORT>0011184948</ns0:CHRPOS_SORT>
        <ns0:MERGED_SORT>1</ns0:MERGED_SORT>
    </ns0:DocumentSummary>
    

</ns0:ExchangeSet>\
"""
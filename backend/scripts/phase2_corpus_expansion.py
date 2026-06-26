
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingestion.parsers.parsers import PDFLegalParser
from app.ingestion.validators.validators import LegalCorpusValidator
from app.ingestion.validators.deduplicator import Deduplicator
from app.ingestion.checksum.checksum import generate_file_metadata
from app.ingestion.normalizers.normalizer import LegalNormalizer
from app.ingestion.reports.corpus_metrics import CorpusMetricsCalculator


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_NORMALIZED_DIR = BASE_DIR / "data" / "normalized"
EVIDENCE_DIR = BASE_DIR / "evidence" / "corpus"


def setup_directories():
    DATA_RAW_DIR.mkdir(exist_ok=True, parents=True)
    DATA_NORMALIZED_DIR.mkdir(exist_ok=True, parents=True)
    EVIDENCE_DIR.mkdir(exist_ok=True, parents=True)
    for subdir in ["bns", "bnss", "bsa", "constitution", "acts", "rules", "judgments"]:
        (DATA_RAW_DIR / subdir).mkdir(exist_ok=True)


def process_pdf(pdf_path: Path, act_config: dict):
    print(f"\n{'='*70}")
    print(f"Processing: {pdf_path.name}")
    print(f"{'='*70}")
    
    source_metadata = generate_file_metadata(
        pdf_path,
        source_url=act_config.get("source_url"),
        publication_date=act_config.get("publication_date"),
        version=act_config.get("version"),
        document_type="act",
        parser_version="1.0.0"
    )
    
    parser = PDFLegalParser(pdf_path)
    parse_func = getattr(parser, act_config["parse_func"])
    parsed_act = parse_func()
    
    if not parsed_act.sections:
        print(f"❌ No sections extracted from {pdf_path.name}")
        return None
    
    deduplicator = Deduplicator()
    parsed_act.sections = deduplicator.deduplicate_sections(
        parsed_act.sections,
        parsed_act.short_title
    )
    
    validator = LegalCorpusValidator()
    validation_result = validator.validate_act(parsed_act)
    
    print(f"\nValidation Result for {parsed_act.short_title}:")
    print(f"  Valid: {validation_result['valid']}")
    print(f"  Total Sections: {validation_result['total_sections']}")
    print(f"  Valid Sections: {validation_result['valid_sections']}")
    if validation_result["errors"]:
        print(f"  Errors: {validation_result['errors']}")
    if validation_result["warnings"]:
        print(f"  Warnings: {validation_result['warnings']}")
    
    normalizer = LegalNormalizer()
    normalized_act = normalizer.normalize_act(parsed_act, source_metadata)
    
    normalized_path = normalizer.save_normalized(normalized_act, DATA_NORMALIZED_DIR)
    print(f"\n✓ Normalized data saved to: {normalized_path}")
    
    validation_report_path = EVIDENCE_DIR / f"validation_{parsed_act.short_title.lower().replace(' ', '_')}.json"
    with validation_report_path.open("w", encoding="utf-8") as f:
        json.dump({
            "act": parsed_act.short_title,
            "validation_result": validation_result,
            "source_metadata": source_metadata,
            "generated_at": datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    print(f"✓ Validation report saved to: {validation_report_path}")
    
    return normalized_act


async def main():
    setup_directories()
    
    act_configs = [
        {
            "pdf_path": DATA_RAW_DIR / "bns" / "bns.pdf",
            "parse_func": "parse_bns",
            "source_url": "https://www.indiacode.nic.in",
            "publication_date": "2023-08-11",
            "version": "1.0"
        },
        {
            "pdf_path": DATA_RAW_DIR / "bnss" / "bnss.pdf",
            "parse_func": "parse_bnss",
            "source_url": "https://www.indiacode.nic.in",
            "publication_date": "2023-08-11",
            "version": "1.0"
        },
        {
            "pdf_path": DATA_RAW_DIR / "bsa" / "bsa.pdf",
            "parse_func": "parse_bsa",
            "source_url": "https://www.indiacode.nic.in",
            "publication_date": "2023-08-11",
            "version": "1.0"
        }
    ]
    
    normalized_acts = []
    for config in act_configs:
        if config["pdf_path"].exists():
            normalized_act = process_pdf(config["pdf_path"], config)
            if normalized_act:
                normalized_acts.append(normalized_act)
        else:
            print(f"\n⚠️ {config['pdf_path']} not found, skipping.")
    
    if normalized_acts:
        print(f"\n{'='*70}")
        print(f"Calculating Corpus Metrics")
        print(f"{'='*70}")
        metrics_calculator = CorpusMetricsCalculator()
        corpus_metrics = metrics_calculator.calculate_corpus_metrics(normalized_acts)
        
        metrics_path = EVIDENCE_DIR / "corpus_metrics.json"
        metrics_calculator.save_metrics(corpus_metrics, metrics_path)
        
        print(f"\n✓ Corpus Metrics:")
        print(f"  Acts: {corpus_metrics['acts']}")
        print(f"  Sections: {corpus_metrics['sections']}")
        print(f"  Total Tokens: {corpus_metrics['total_tokens']}")
        print(f"  Total Characters: {corpus_metrics['total_characters']}")
        print(f"  Duplicates: {corpus_metrics['duplicate_count']}")
        print(f"  Metrics saved to: {metrics_path}")
        
        log_path = EVIDENCE_DIR / "ingestion_log.json"
        with log_path.open("w", encoding="utf-8") as f:
            json.dump({
                "status": "success",
                "acts_processed": len(normalized_acts),
                "acts": [act["short_title"] for act in normalized_acts],
                "generated_at": datetime.now().isoformat(),
                "corpus_metrics": corpus_metrics
            }, f, indent=2, ensure_ascii=False)
        print(f"✓ Ingestion log saved to: {log_path}")
    
    print(f"\n{'='*70}")
    print(f"✅ Phase 2 Corpus Expansion Complete!")
    print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())

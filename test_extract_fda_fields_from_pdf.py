from pathlib import Path
from src.modules.competitive_analysis.create_competitive_analysis_detail import create_competitive_analysis_detail


document_path = Path('/Users/macbookpro/Documents/boleary_fda/ivd_decision_summaries_2010s/K181201.pdf')

if __name__ == "__main__":
    result = create_competitive_analysis_detail(document_path)
    print(result)

from Bio import Entrez
import os

# Set email if available, otherwise use dummy
Entrez.email = os.environ.get("ENTREZ_EMAIL", "proteintoolbox@example.com")

def search_pubmed(query: str, max_results: int = 5) -> str:
    """
    Searches PubMed for a query and returns titles and IDs.
    
    Args:
        query (str): Search term.
        max_results (int): Number of abstracts to fetch.
        
    Returns:
        str: Formatted list of papers.
    """
    try:
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        
        id_list = record["IdList"]
        if not id_list:
            return "No results found."
            
        handle = Entrez.efetch(db="pubmed", id=id_list, rettype="medline", retmode="text")
        papers = handle.read()
        handle.close()
        
        # Simple parsing or just return raw text
        return papers[:2000] + "..." if len(papers) > 2000 else papers
    except Exception as e:
        return f"Error searching PubMed: {e}"

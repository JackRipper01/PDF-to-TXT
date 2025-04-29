import os
import PyPDF2
import sys
import re
import shutil

def convert_pdf_to_txt(pdf_path, txt_path, filter_references=True):
    """
    Convert a PDF file to a text file
    
    Args:
        pdf_path (str): Path to the PDF file
        txt_path (str): Path where the text file will be saved
        filter_references (bool): Whether to filter out the references section and beyond
    """
    try:
        # Open the PDF file in read-binary mode
        with open(pdf_path, 'rb') as pdf_file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from each page
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            # Filter out references and acknowledgments sections if requested
            if filter_references:
                # Look for the references section using common patterns
                # More flexible patterns to catch various formats
                reference_patterns = [
                    r'\nREFERENCES\s*\n',
                    r'\nReferences\s*\n',
                    r'\nReference\s*\n',
                    r'\nREFERENCE\s*\n',
                    r'\nBIBLIOGRAPHY\s*\n',
                    r'\nWORKS CITED\s*\n',
                    r'\nCITED WORKS\s*\n',
                    r'\nLITERATURE CITED\s*\n',
                    r'REFERENCES\s*\n',  # Without leading newline
                    r'REFERENCE\s*\n',   # Without leading newline
                    r'BIBLIOGRAPHY\s*\n', # Without leading newline
                    r'\nR\s*E\s*F\s*E\s*R\s*E\s*N\s*C\s*E\s*S\s*\n',  # Spaced out
                    r'R\s*E\s*F\s*E\s*R\s*E\s*N\s*C\s*E\s*S\s*\n',    # Spaced out without newline
                    r'\[\s*REFERENCES\s*\]',  # With brackets
                    r'\d+\.\s*REFERENCES',    # Numbered section
                ]
                
                # Look for acknowledgments section patterns
                acknowledgment_patterns = [
                    r'\nACKNOWLEDGMENTS\s*\n',
                    r'\nACKNOWLEDGMENT\s*\n',
                    r'\nACKNOWLEDGEMENT\s*\n',
                    r'\nACKNOWLEDGEMENTS\s*\n',
                    r'ACKNOWLEDGMENTS\s*\n',  # Without leading newline
                    r'ACKNOWLEDGMENT\s*\n',   # Without leading newline
                    r'ACKNOWLEDGEMENT\s*\n',  # Without leading newline
                    r'ACKNOWLEDGEMENTS\s*\n', # Without leading newline
                    r'\nA\s*C\s*K\s*N\s*O\s*W\s*L\s*E\s*D\s*G\s*M\s*E\s*N\s*T\s*S\s*\n',  # Spaced out
                    r'A\s*C\s*K\s*N\s*O\s*W\s*L\s*E\s*D\s*G\s*M\s*E\s*N\s*T\s*S\s*\n',    # Spaced out without newline
                ]
                
                # Combine all patterns to find the earliest occurrence
                all_patterns = reference_patterns + acknowledgment_patterns
                
                # Find the position of the earliest section to remove
                cutoff_position = float('inf')
                for pattern in all_patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)  # Case insensitive matching
                    for match in matches:
                        if match.start() < cutoff_position:
                            cutoff_position = match.start()
                
                # If any section is found, truncate the text
                if cutoff_position != float('inf'):
                    text = text[:cutoff_position]
            
            # Write the extracted text to a file
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
                
            print(f"Successfully converted {os.path.basename(pdf_path)} to text")
            return True
    except Exception as e:
        print(f"Error converting {os.path.basename(pdf_path)}: {str(e)}")
        return False

def process_directory(input_dir, output_dir, base_input_dir=None):
    """
    Process a directory recursively, converting all PDF files to text
    
    Args:
        input_dir (str): Path to the input directory
        output_dir (str): Path to the output directory
        base_input_dir (str): Base input directory for relative path calculation
    """
    # Set base input directory on first call
    if base_input_dir is None:
        base_input_dir = input_dir
    
    # Create a subfolder in the output directory to store converted files
    rel_path = os.path.relpath(input_dir, base_input_dir)
    if rel_path == '.':
        # For the root directory
        current_output_dir = os.path.join(output_dir, "converted_txt")
    else:
        # For subdirectories
        current_output_dir = os.path.join(output_dir, rel_path, "converted_txt")
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(current_output_dir):
        os.makedirs(current_output_dir)
        print(f"Created output directory: {current_output_dir}")
    
    # Get all PDF files in the current directory
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    # Convert each PDF file to text
    successful_conversions = 0
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        txt_file = os.path.splitext(pdf_file)[0] + '.txt'
        txt_path = os.path.join(current_output_dir, txt_file)
        
        if convert_pdf_to_txt(pdf_path, txt_path, filter_references=True):
            successful_conversions += 1
    
    # Print summary for current directory
    if pdf_files:
        print(f"\nDirectory {input_dir}: {successful_conversions} out of {len(pdf_files)} files converted successfully.")
    
    # Process subdirectories
    for item in os.listdir(input_dir):
        item_path = os.path.join(input_dir, item)
        if os.path.isdir(item_path):
            process_directory(item_path, output_dir, base_input_dir)

def main():
    # Define input and output directories
    # Modified to work from the src directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)  # Go up one level to the project root
    input_dir = os.path.join(project_dir, "input")
    output_dir = os.path.join(project_dir, "output")
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' does not exist. Creating it...")
        os.makedirs(input_dir)
    
    # Check if output directory exists
    if not os.path.exists(output_dir):
        print(f"Output directory '{output_dir}' does not exist. Creating it...")
        os.makedirs(output_dir)
    
    # Process the input directory recursively
    process_directory(input_dir, output_dir)
    
    print("\nConversion process completed.")

if __name__ == "__main__":
    main()
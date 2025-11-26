
import json
import subprocess
import os
import shutil

class PDFGenerator:
    def __init__(self, template_path="src/templates/report_template.typ", output_dir="generated_reports"):
        self.template_path = template_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(self, report_data, filename):
        """
        Generates a PDF report using Typst.
        
        Args:
            report_data (dict): Data to be used in the report.
            filename (str): Output filename (e.g., "report_123.pdf").
            
        Returns:
            str: Path to the generated PDF.
        """
        # 1. Prepare paths
        # Typst needs the JSON data file to be accessible relative to the .typ file
        # We'll work in the output directory to keep things clean
        
        # Path for the temporary JSON data file
        json_filename = f"data_{filename.replace('.pdf', '.json')}"
        json_path = os.path.join(self.output_dir, "report_data.json") # Fixed name as per template
        
        # Path for the temporary Typst file
        typ_filename = f"temp_{filename.replace('.pdf', '.typ')}"
        typ_path = os.path.join(self.output_dir, typ_filename)
        
        output_pdf_path = os.path.join(self.output_dir, filename)

        # 2. Write Data JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        # 3. Copy/Write Template
        # We need to modify the template to point to our specific json file if we run multiple concurrently?
        # For now, the template hardcodes "report_data.json". 
        # So we must use that name and run sequentially or use separate dirs.
        # For simplicity, we use a fixed json name and assume sequential or isolated execution.
        
        shutil.copy(self.template_path, typ_path)
        
        # 4. Run Typst
        # We need to run typst from the output_dir so it finds the json file
        typst_bin = os.path.abspath(".venv_wsl/bin/typst")
        if not os.path.exists(typst_bin):
            typst_bin = "typst" # Try global path

        cmd = [typst_bin, "compile", os.path.basename(typ_path), filename]
        
        print(f"🚀 Running Typst: {' '.join(cmd)} in {self.output_dir}")
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.output_dir, # Run inside output dir
                capture_output=True, 
                text=True, 
                check=True
            )
            print(f"✅ PDF Generated: {output_pdf_path}")
            
            # Cleanup temp files
            # os.remove(json_path)
            # os.remove(typ_path)
            
            return output_pdf_path
        except subprocess.CalledProcessError as e:
            print(f"❌ Typst Error: {e.stderr}")
            print(f"   Stdout: {e.stdout}")
            raise e

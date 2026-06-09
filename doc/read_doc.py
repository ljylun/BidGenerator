import win32com.client
import os
import sys

filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '招标正文.doc')

word = win32com.client.Dispatch('Word.Application')
word.Visible = False

output_lines = []

try:
    doc = word.Documents.Open(filepath)
    
    for p in doc.Paragraphs:
        text = p.Range.Text.strip()
        if text:
            output_lines.append(text)
    
    output_lines.append('\n\n=== TABLES ===\n')
    
    for i in range(doc.Tables.Count):
        table = doc.Tables.Item(i + 1)
        output_lines.append(f'--- TABLE_{i} ---')
        for row in range(table.Rows.Count):
            cells = []
            for col in range(table.Columns.Count):
                try:
                    cell_text = table.Cell(row + 1, col + 1).Range.Text
                    cell_text = cell_text.replace('\r\n', ' ').replace('\r', ' ').replace('\x07', ' ').strip()
                    cells.append(cell_text)
                except Exception:
                    try:
                        # fallback: get all text from row
                        row_text = table.Rows.Item(row + 1).Range.Text.strip()
                        cells = [row_text]
                        break
                    except:
                        cells.append('')
            if cells:
                output_lines.append(' | '.join(cells))
        output_lines.append(f'--- END_TABLE_{i} ---')
    
    doc.Close(False)
    
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doc_content.txt')
    with open(out_path, 'w', encoding='utf-8') as out:
        for line in output_lines:
            out.write(line + '\n')
    
    print("OK")
except Exception as e:
    print(f"ERROR: {e}")
    # still try to save what we have
    try:
        out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doc_content.txt')
        with open(out_path, 'w', encoding='utf-8') as out:
            for line in output_lines:
                out.write(line + '\n')
        print(f"Partial content saved, {len(output_lines)} lines")
    except:
        pass
finally:
    try:
        word.Quit()
    except:
        pass

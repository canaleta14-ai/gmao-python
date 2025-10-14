import openpyxl

excel_path = "Proveedores.xlsx"
wb = openpyxl.load_workbook(excel_path)
sheet = wb.active

columns = [cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1))]
print("Columnas detectadas en el Excel:")
for col in columns:
    print(col)
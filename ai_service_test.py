from ai_service.ai_service import process_document

result = process_document("C:/Users/yishu/Downloads/IVD Dummy Device Description.pdf") #embed=True

print("Summary:\n", result["summary"])
print("Missing QA items:", result["missing_questions"])
#print("Missing template fields:", result["missing_template_fields"])

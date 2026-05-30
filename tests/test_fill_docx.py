#!/usr/bin/env python3
"""
Test script for fill_template_docx function with mock prior authorization data.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.utils.fill_template_docx import fill_template_docx

# Mock data simulating the output from prior_auth_handler
# mock_data = {
#     "request_type": "Initial Request",
#     "pre_scheduled_date_of_service": "2026-06-15",
#     "authorization_needed_by_date": "2026-06-10",
#     "expedited_request_physician_signature": "Dr. Emily Carter",
#     "member_last_name": "Smith",
#     "member_first_name": "John A.",
#     "member_id": "BC123456789",
#     "date_of_birth": "1972-03-14",
#     "gender": "M",
#     "req_provider_name": "Dr. Emily Carter, MD",
#     "req_provider_num_or_tax_id": "TAX-987654",
#     "req_provider_npi": "1234567890",
#     "req_provider_phone": "(555) 123-4567",
#     "req_provider_fax": "(555) 123-4568",
#     "req_provider_contact_person": "Jane Doe",
#     "service_provider_name": "Sample General Hospital",
#     "service_provider_address": "123 Medical Center Dr, Healthcare City, HC 12345",
#     "service_provider_tax_id": "TAX-123456",
#     "service_provider_npi": "9876543210",
#     "service_provider_phone": "(555) 987-6543",
#     "service_provider_fax": "(555) 987-6544",
#     "service_provider_contact_person": "John Admin",
#     "requested_service_types": ["pain_management"],
#     "clinical_trial_type": None,
#     "diagnosis": [
#         {
#             "code": "M54.16",
#             "description": "Lumbar radiculopathy, left L5 distribution"
#         },
#         {
#             "code": "M99.23",
#             "description": "Severe lumbar foraminal stenosis at L4-L5"
#         },
#         {
#             "code": "M54.5",
#             "description": "Chronic low back pain refractory to conservative therapy"
#         }
#     ],
#     "procedure": [
#         {
#             "code": "62311",
#             "description": "Lumbar epidural steroid injection under fluoroscopic guidance"
#         }
#     ],
#     "supporting_chart_notes_available": True,
#     "diagnostic_tests_summary": "MRI Lumbar Spine performed on 04/18/2026 demonstrated severe left-sided L4-L5 foraminal stenosis with nerve root impingement and moderate degenerative disc disease.",
#     "lab_values_summary": None,
#     "medical_necessity_statement": "The requested procedure is medically necessary due to severe pain, documented neurologic deficits, functional impairment, and failure of conservative management. Without intervention, the patient is at increased risk for worsening mobility limitations and reduced quality of life.",
#     "failed_conservative_treatments": [
#         "physical therapy",
#         "NSAIDs (Ibuprofen)",
#         "oral steroids",
#         "home exercise program",
#         "Gabapentin"
#     ],
#     "functional_impairment_description": "Persistent lower back pain radiating to the left leg with worsening functional limitation. Patient reports difficulty performing activities of daily living and inability to sit for extended periods while working. Limited lumbar range of motion secondary to pain. Positive straight leg raise on left at 40 degrees. Mild decreased sensation along L5 dermatome on left side. Motor strength 4/5 in left dorsiflexion. Antalgic gait noted.",
#     "additional_notes": []
# }

mock_data = {
    "request_type": None,
    "pre_scheduled_date_of_service": None,
    "authorization_needed_by_date": None,
    "expedited_request_physician_signature": None,
    "member_last_name": "Smith",
    "member_first_name": "John A.",
    "member_id": None,
    "date_of_birth": "1972-03-14",
    "gender": "M",
    "req_provider_name": "Emily Carter",
    "req_provider_num_or_tax_id": None,
    "req_provider_npi": None,
    "req_provider_phone": None,
    "req_provider_fax": None,
    "req_provider_contact_person": None,
    "service_provider_name": "Sample General Hospital",
    "service_provider_address": None,
    "service_provider_tax_id": None,
    "service_provider_npi": None,
    "service_provider_phone": None,
    "service_provider_fax": None,
    "service_provider_contact_person": None,
    "requested_service_types": [
        "pain_management"
    ],
    "clinical_trial_type": None,
    "diagnosis": [
        {
            "code": None,
            "description": "Lumbar radiculopathy, left L5 distribution"
        },
        {
            "code": None,
            "description": "Severe lumbar foraminal stenosis at L4-L5"
        },
        {
            "code": None,
            "description": "Chronic low back pain refractory to conservative therapy"
        }
    ],
    "procedure": [
        {
            "code": None,
            "description": "lumbar epidural steroid injection under fluoroscopic guidance"
        }
    ],
    "supporting_chart_notes_available": True,
    "diagnostic_tests_summary": "MRI Lumbar Spine performed on 04/18/2026 demonstrated severe left-sided L4-L5 foraminal stenosis with nerve root impingement and moderate degenerative disc disease.",
    "lab_values_summary": None,
    "medical_necessity_statement": "The requested procedure is medically necessary due to severe pain, documented neurologic deficits, functional impairment, and failure of conservative management. Without intervention, the patient is at increased risk for worsening mobility limitations and reduced quality of life.",
    "failed_conservative_treatments": [
        "physical therapy",
        "NSAIDs",
        "oral steroids",
        "home exercise program"
    ],
    "functional_impairment_description": "difficulty performing activities of daily living and inability to sit for extended periods while working.",
    "additional_notes": []
}

def main():
    print("Testing fill_template_docx function...")
    print("=" * 60)
    
    # Paths
    template_path = Path("app/data/templates/prior_authorization_template.docx")
    output_path = Path("app/data/test_filled_prior_authorization.docx")
    
    # Check if template exists
    if not template_path.exists():
        print(f"❌ Error: Template file not found at {template_path}")
        return 1
    
    print(f"✓ Template found: {template_path}")
    print(f"✓ Output will be saved to: {output_path}")
    print()
    
    # Print mock data summary
    print("Mock Data Summary:")
    print(f"  - Patient: {mock_data['member_first_name']} {mock_data['member_last_name']}")
    print(f"  - DOB: {mock_data['date_of_birth']}")
    print(f"  - Provider: {mock_data['req_provider_name']}")
    print(f"  - Diagnoses: {len(mock_data['diagnosis'])} items")
    print(f"  - Procedures: {len(mock_data['procedure'])} items")
    print(f"  - Failed Treatments: {len(mock_data['failed_conservative_treatments'])} items")
    print()
    
    try:
        # Call the function
        print("Filling template...")
        result_path = fill_template_docx(
            template_path=str(template_path),
            data=mock_data,
            output_path=str(output_path)
        )
        
        print(f"✓ Success! Document created at: {result_path}")
        print()
        print("Please open the document to verify that placeholders were replaced correctly.")
        print()
        
        # Verify file exists
        if Path(result_path).exists():
            file_size = Path(result_path).stat().st_size
            print(f"✓ File verified: {file_size:,} bytes")
            return 0
        else:
            print("❌ Error: Output file was not created")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
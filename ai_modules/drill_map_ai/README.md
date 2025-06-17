# Drill Map AI Module

This module is responsible for processing and classifying drill map images using AI techniques.
# Overview
It utilizes a pre-trained model to classify images and extract relevant information from them.
# Features
- Image classification using a pre-trained model.
- OCR (Optical Character Recognition) capabilities for text extraction.
- Support for multiple drill map formats and configurations.
# Installation
To install the Drill Map AI module, follow these steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/drill_map_ai.git
   ```
2. Install the required dependencies:
   ```bash
   cd drill_map_ai
   pip install -r requirements.txt
   ```
3. Run the module:
   ```bash
   uvicorn main:app --reload
   ```
# Usage
To use the Drill Map AI module, you can send a POST request to the `/classify` endpoint with the image file in the request body. The module will return the classification results and any extracted text.
# Example Request
```bash
curl -X POST "http://localhost:8000/drill_map/classify" -H "Content-Type: application/json" -d '{
  "img_src": "data:image/jpeg;base64,...",
  "product_name": "A287570_"
}'
```
# Example Response
```json
{
  "classification_code": "TYPE0、TYPE1、TYPE3、TYPE4、N/A、UNKNOW",
  "classification_model": "Inference Model",
  "distance" : -1
}
```

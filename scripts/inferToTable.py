import os
import cv2
import pandas as pd
import layoutparser as lp
from img2table.ocr import PaddleOCR
from img2table.document import Image

# Load model
model = lp.models.Detectron2LayoutModel(
    config_path= f"G:\My Drive\SKU\Models and Configurations\strauss\config.yaml",
    model_path= f"G:\My Drive\SKU\Models and Configurations\strauss\model_final.pth",
    extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.4])

# Infer on data
path = f"D:\SKU-Garments\data\Square documents sorted\STRAUSS jpg\PO1086979 - July order - ETD 16-11-2021_1.jpg"
img = cv2.imread(path)
layout = model.detect(img)
# lp.draw_box(img, layout, color_map={0: "red", 1: "blue", 2: "green", 3: "brown"})

# Create metadata
metadata = []
for idx, block in enumerate(layout):
    label_info = {
        "id": idx,
        "coordinates": {
            "x1": block.coordinates[0],
            "y1": block.coordinates[1],
            "x2": block.coordinates[2],
            "y2": block.coordinates[3]
        },
        "type": block.type,
        "score": block.score
    }
    metadata.append(label_info)
# print("\n", metadata[0], "\n", metadata[1], "\n", metadata[2])

# Label Map for STRAUSS
label_map = {0: "number", 1: "date", 2: "table"}
for data in metadata:
    if data['type'] == 2: # label number '2' corresponds to the labels for the class 'table' for STRAUSS
        x1 = int(data['coordinates']['x1'])
        x2 = int(data['coordinates']['x2'])
        y1 = int(data['coordinates']['y1'])
        y2 = int(data['coordinates']['y2'])
        # print(f"Detected box: {label_map[data['type']]}")
        # print(f"Coordinates: {x1}, {y1}, {x2}, {y2}")

        crop = img[y1:y2, x1:x2]
        crop_height, crop_width = crop.shape[:2]
        target_h, target_w = 600, 800
        resized = cv2.resize(crop, (target_w, target_h), interpolation=cv2.INTER_AREA)
        cv2.imwrite("D:/SKU-Garments/scripts/testData/table.jpg", crop)
        # print("Cropped Image shape:", crop.shape)
        # print("Resized Image shape: ", resized.shape)
        # cv2.imshow("Cropped Image", resized)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # Extract tabular data
        src = "D:/SKU-Garments/scripts/testData/table.jpg"
        os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
        img = Image(src, detect_rotation=True)
        ocr = PaddleOCR(lang="en")
        # Extraction of tables and creation of a xlsx file containing tables
        img.to_xlsx(dest="D:/SKU-Garments/scripts/testData/table.xlsx",
                    ocr=ocr,
                    implicit_rows=True,
                    implicit_columns=True,
                    borderless_tables=True,
                    min_confidence=50)
        # View the tabular data as a DataFrame
        df = pd.read_excel("D:/SKU-Garments/scripts/testData/table.xlsx")
        print(df)
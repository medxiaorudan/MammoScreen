# MammoScreenApp

MammoScreenApp is a simple image labeler application designed to assist users in labeling images, especially medical images in DICOM format. The application provides a GUI interface for loading, viewing, and labeling images.

## Features

- Load images from a directory.
- Support for common image formats (JPG, JPEG, PNG, BMP) and DICOM format.
- Label images as 'Y' or 'N'.
- Save labeling history to a file.
- Simple and intuitive GUI interface.

## Installation

1. Clone the repository:
```
git clone https://github.com/medxiaorudan/MammoScreen.git
```
2. Navigate to the repository directory:
```
cd  MammoScreen
```
3. Install the required packages:
```
pip install -r requirements.txt
```

## Usage

1. Run the script:
```
python MammoScreen.py
```

2. Use the "Load Images" button to select a directory containing the images you want to label.
3. Label the images using the 'Y' or 'N' buttons.
<p float="left">
  <img src="./images/image1.PNG" width="500" />
</p>
5. Once done, click on the "Finish Labeling" button to save the labels.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)

+------------------------+    +----------------------+    +----------------------+
|   Preprocess with LLM  | -> |   Improved Code      | -> |  Feedback to LLM    |
+------------------------+    | Generation based on |    |  (VCs and Analysis) |
             |                 | Feedback from Frama- |    |                      |
             v                 | C and LLM            |    +----------------------+
+------------------------+    +----------------------+    +----------------------+
|        Frama-C         | <- |   Training Results   | <- |    PPO Training     |
|    Static Analysis     |    |    from PPO           |    |                      |
|                        |    +----------------------+    +----------------------+
+------------------------+             |                      |
             |                         v                      |
             |             +----------------------+          |
             +------------>| Improved Environment | <--------+
                           | and Policy from PPO  |
                           +----------------------+

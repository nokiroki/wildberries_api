# Wildberries API

## Description

Repo for downloading and modifying data from Wildberries.

## Prerequirements

Install required libraries with `pip install -r requirements.txt`

## Modes

The mode is selected using `-m` or `--mode` key:

| Mode          | Description | Additioinal keys |
| ------------- | ----------- | ---------------- |
| `save`          | Saving cards information by required list ||
| `modify`        | Modifying existing vendors | `-d` - will set default values for existing sizes |
| `get_prices`    | Get prices for vendors ||
| `upload_images` | Upload images from computer to the wildberries | `-g` - Consider image path as global |
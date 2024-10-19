## Description
This script allows to send markdown content from a link containint the raw text to a desire **Outline Wiki** document.
I used [this API request](https://www.getoutline.com/developers#tag/documents/POST/documents.update) from Outline.

## Usage
First, ensure you have all dependencies installed
```bash
$ pip install requests urllib3 
```
Now you can run it with:
```bash
$ python3 outline_send.py -f FILE.json [-a/--append]
```
> [!Note] 
> The `--append` toggle is set globally for all the sends targeted in the JSON file.
> This might be changed in the future so it can be set for each individual send.
### Example configuration file:

```json
{
   "outline_api" : "SECRET_API_KEY",
   "data" : [
    {
        "source": "https://raw.file.com/file.md",
        "destination": "https://your.outline.app/doc/name"
    },
    {
        "source": "https://raw.file.com/file2.md",
        "destination": "https://your.outline.app/doc/name2"
    } 
   ]
}
```
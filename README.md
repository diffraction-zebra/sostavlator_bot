# Taskify
## How to launch
Modify `src/taskify/secrets.py` with your own credentials.

```bash
docker build -t taskify .
docker run --rm -v $(pwd)/data:/app/data taskify
```

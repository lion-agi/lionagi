to run codebase concation and compression

1. ensure you have `uv` installed in your environment. You can install it using
   pip:
   ```bash
   pip install uv
   ```
2. the scipt use `OpenRouter` to conduct compression, you need to have
   `OPENROUTER_API_KEY` set in your `.env`. You can get it from
   [OpenRouter](https://openrouter.ai/).

3. install the required dependencies
   ```bash
   uv run scripts/concat.py
   ```

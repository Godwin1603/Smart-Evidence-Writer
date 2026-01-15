# TODO: Update ai_analyzer.py for vertexai==1.71.1 compatibility

## Steps to Complete

- [x] Update model initialization: Replace `GenerativeModel(VERTEX_AI_MODEL)` with `TextGenerationModel.from_pretrained("text-bison-001")`
- [x] Remove all `Part` references: Eliminate `Part.from_data` and `Part.from_text` usages in `analyze_evidence`
- [x] Adapt multimedia handling: For non-text files, rely on metadata only in prompts, do not read binary data
- [x] Update AI call: Change `model.generate_content([full_prompt, part], generation_config=...)` to `model.predict(prompt=full_prompt, temperature=0.2, top_p=0.8, top_k=40, max_output_tokens=2048)`
- [ ] Verify functionality: Ensure Evidence Chat, summarization, and report generation remain intact
- [ ] Test compatibility: Confirm works with Python 3.13 and GCP Vertex AI setup

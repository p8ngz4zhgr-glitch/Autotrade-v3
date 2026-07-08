with open("bot_code/analyzer/main_scanner.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "_PIPELINE_SEMAPHORE = threading.Semaphore(" in line:
        lines[i] = '    _PIPELINE_SEMAPHORE = threading.Semaphore(4)  # Tăng lên 4 luồng song song\n'
        break

# Lọc sớm ở hàm _run_pipeline_sync
# We find `def _run_pipeline_sync(self, sym, data):`
for i, line in enumerate(lines):
    if "def _run_pipeline_sync(self, sym, data):" in line:
        # replace the original if statement
        # Original:
        # if data.get("final") == "WAIT" and data.get("confidence", 0) < 70:
        #     return
        lines[i+1] = '        final_sig = data.get("final", "WAIT")\n'
        lines.insert(i+2, '        conf = data.get("confidence", 0)\n')
        lines.insert(i+3, '        ev_ratio = data.get("bayes_ev", {}).get("ev_ratio", 0)\n')
        lines.insert(i+4, '        if final_sig == "WAIT" and conf < 70 and ev_ratio < 0.3:\n')
        lines.insert(i+5, '            return\n')
        break

# Lọc sớm trước LLM ở def _scan
for i, line in enumerate(lines):
    if 'data["ai_memory"] = get_memory_for_ai(sym)' in line:
        # Chèn lọc sớm trước llm.analyze
        insert_code = """
                final_sig = data.get("final", "WAIT")
                conf = data.get("confidence", 0)
                ev_ratio = data.get("bayes_ev", {}).get("ev_ratio", 0)
                
                # [LỌC SỚM TÀI NGUYÊN] Bỏ qua AI cho lệnh WAIT có toán học quá yếu
                if final_sig == "WAIT" and ev_ratio < 0.2 and conf < 65:
                    self.log.info("  ⏭️ [Early Filter] Bỏ qua AI cho %s (EV: %.2f, Conf: %.1f%%) để tiết kiệm server", sym, ev_ratio, conf)
                    time.sleep(1.0)
                    continue
"""
        lines.insert(i+1, insert_code)
        break

with open("bot_code/analyzer/main_scanner.py", "w") as f:
    f.writelines(lines)
print("Patched main_scanner.py")

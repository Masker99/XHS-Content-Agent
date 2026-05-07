from __future__ import annotations

import argparse

from xhs_agent import format_result, run_xhs_workflow, stream_xhs_workflow


def run_once(instruction: str, stream: bool) -> None:
    if stream:
        latest = {}
        for event in stream_xhs_workflow(instruction):
            for node_name, value in event.items():
                latest.update(value)
                print(f"\n--- {node_name} 完成 ---")
                if node_name == "build_framework":
                    print(value.get("framework", ""))
                elif node_name == "generate_titles":
                    print(value.get("titles", ""))
                elif node_name == "select_title":
                    print(value.get("selected_title", ""))
                elif node_name == "generate_keywords":
                    print(value.get("keywords", ""))
                elif node_name == "humanize_copy":
                    print(value.get("final_copy", ""))
                elif node_name == "generate_cover_prompt":
                    print(value.get("cover_prompt", ""))
        return

    result = run_xhs_workflow(instruction)
    print(format_result(result))


def interactive() -> None:
    print("XHS LangGraph workflow ready. 输入 quit / exit / q 退出。")
    while True:
        try:
            user_input = input("\nOpenClaw/User 指令: ").strip()
        except EOFError:
            break

        if user_input.lower() in {"quit", "exit", "q"}:
            print("Goodbye.")
            break
        if not user_input:
            continue

        try:
            run_once(user_input, stream=True)
        except Exception as exc:
            print(f"Error: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the XHS LangGraph workflow.")
    parser.add_argument("instruction", nargs="?", help="Plain text or OpenClaw JSON payload.")
    parser.add_argument("--stream", action="store_true", help="Print node output as each step finishes.")
    args = parser.parse_args()

    if args.instruction:
        run_once(args.instruction, stream=args.stream)
    else:
        interactive()


if __name__ == "__main__":
    main()

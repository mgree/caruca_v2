# --- naive-arm welcome (installed by new_run_vm.sh) ---
case $- in *i*)
  cd ~/naive-arm 2>/dev/null
  cat <<'WELCOME'

  Naive Claude Code arm — this VM is a throwaway clone of naive-golden. You are in ~/naive-arm.

    naive-run <command> [PROMPT_vN.md]      headless run, full log in runs/<command>_<version>.jsonl
    naive-run -i <command> [PROMPT_vN.md]   interactive run (watch it, answer its prompts)

  Prompt versions: PROMPT_v1.md (bare)  PROMPT_v2.md (execution guidance). Default: v1.
  Not allowed as test commands: tee uniq grep rm (they are the samples).
  One run per clone. When done: exit, then on the Mac
    ./collect_run.sh <this VM's name>      copies output/ and runs/ into the repo and deletes the clone

WELCOME
  ;;
esac
# --- end naive-arm welcome ---

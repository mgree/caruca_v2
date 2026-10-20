# --- naive-arm welcome (installed by new_run_vm.sh) ---
case $- in *i*)
  cd ~/naive-arm 2>/dev/null
  cat <<'WELCOME'

  Naive Claude Code arm — this VM is a throwaway clone of naive-golden. You are in ~/naive-arm.

    naive-run <command> [PROMPT_vN.md]      runs unattended, shows every tool call / input / result live;
                                            everything about the run lands in its own ~/runs/<date>_<time>_…/
    naive-run -i <command> [PROMPT_vN.md]   Claude Code's own interactive screen (press Enter to send the prompt)

  Prompt versions (in ~/prompts, outside the work folder): PROMPT_v1.md (bare)  PROMPT_v2.md (execution guidance). Default: v1.
  Core nine: cat grep pwd rm tac tail tee uniq wc. Anything else asks for confirmation first.
  Model: claude-fable-5-1 at medium effort if this account can use it, else claude-opus-5-5 at high.
  Web search/fetch tools and MCP servers are off; any URL in the session's Bash commands is listed in bash_urls.txt.
  tee uniq grep rm are also the samples, so for them the session can see a finished answer.
  Each invocation gets its own run folder; a second run in this clone is marked as not fresh. When done: exit, then on the Mac
    ./collect_run.sh <this VM's name>      copies every run folder into the package's runs/ and deletes the clone

WELCOME
  ;;
esac
# --- end naive-arm welcome ---

#!/usr/bin/env bash
set -euo pipefail

RC_BLOCK_BEGIN="# >>> codex feat-wt >>>"
RC_BLOCK_END="# <<< codex feat-wt <<<"

detect_shell_kind() {
  # Try to infer the user's *interactive* shell.
  # - When invoked via kickoff.sh, the direct parent is usually `bash`,
  #   so we also inspect the grandparent.
  local parent_comm parent_pid grandparent_pid grandparent_comm shell_env

  parent_comm="$(ps -p "${PPID}" -o comm= 2>/dev/null | tr -d '[:space:]' || true)"
  parent_pid="${PPID}"
  grandparent_pid="$(ps -p "${parent_pid}" -o ppid= 2>/dev/null | tr -d '[:space:]' || true)"
  grandparent_comm=""
  if [[ -n "${grandparent_pid}" ]]; then
    grandparent_comm="$(ps -p "${grandparent_pid}" -o comm= 2>/dev/null | tr -d '[:space:]' || true)"
  fi

  if [[ "${parent_comm}" == "bash" ]]; then
    case "${grandparent_comm}" in
      zsh|fish)
        echo "${grandparent_comm}"
        return 0
        ;;
    esac
  fi

  case "${parent_comm}" in
    zsh|bash|fish)
      echo "${parent_comm}"
      return 0
      ;;
  esac

  shell_env="$(basename "${SHELL:-}" 2>/dev/null || true)"
  case "${shell_env}" in
    zsh|bash|fish)
      echo "${shell_env}"
      return 0
      ;;
  esac

  echo "unknown"
}

_rc_file_for_shell() {
  local shell_kind
  shell_kind="$(detect_shell_kind)"
  case "${shell_kind}" in
    zsh)
      echo "${HOME}/.zshrc"
      ;;
    bash)
      if [[ -f "${HOME}/.bashrc" ]]; then
        echo "${HOME}/.bashrc"
      elif [[ -f "${HOME}/.bash_profile" ]]; then
        echo "${HOME}/.bash_profile"
      else
        echo "${HOME}/.bashrc"
      fi
      ;;
    fish)
      echo "${HOME}/.config/fish/config.fish"
      ;;
    *)
      echo "${HOME}/.profile"
      ;;
  esac
}

_rc_block_payload() {
  local shell_kind codex_bin
  shell_kind="$(detect_shell_kind)"
  codex_bin="${HOME}/.codex/bin"
  case "${shell_kind}" in
    fish)
      # fish：用 contains guard，避免重复插入路径
      cat <<EOF
if not contains -- "${codex_bin}" \$PATH
  set -gx PATH "${codex_bin}" \$PATH
end
EOF
      ;;
    *)
      cat <<EOF
export PATH="${codex_bin}:\$PATH"
EOF
      ;;
  esac
}

_backup_file_if_exists() {
  local path ts
  path="$1"
  if [[ ! -f "${path}" ]]; then
    return 0
  fi
  ts="$(date '+%Y%m%d-%H%M%S')"
  cp "${path}" "${path}.bak-codex-feat-wt-${ts}"
}

_upsert_rc_block() {
  local rc_file payload tmp payload_file
  rc_file="$1"
  payload="$2"

  mkdir -p "$(dirname "${rc_file}")"
  [[ -f "${rc_file}" ]] || touch "${rc_file}"

  # 若已有人手工配置过 ~/.codex/bin，则不再追加（除非已存在 codex marker block）
  if ! grep -Fq "${RC_BLOCK_BEGIN}" "${rc_file}" 2>/dev/null; then
    if grep -Fq ".codex/bin" "${rc_file}" 2>/dev/null; then
      return 1
    fi
  fi

  tmp="$(mktemp)"
  payload_file="$(mktemp)"
  printf "%s\n" "${payload}" >"${payload_file}"

  if grep -Fq "${RC_BLOCK_BEGIN}" "${rc_file}" 2>/dev/null && grep -Fq "${RC_BLOCK_END}" "${rc_file}" 2>/dev/null; then
    awk -v begin="${RC_BLOCK_BEGIN}" -v end="${RC_BLOCK_END}" -v payload_file="${payload_file}" '
      BEGIN{skip=0; replaced=0}
      $0==begin{
        print begin
        while ((getline line < payload_file) > 0) { print line }
        close(payload_file)
        skip=1
        replaced=1
        next
      }
      $0==end{ skip=0; print end; next }
      skip==0{ print }
      END{}
    ' "${rc_file}" >"${tmp}"
  else
    cat "${rc_file}" >"${tmp}"
    # 确保前面有一行空行，避免贴在最后一行后面
    if [[ -s "${tmp}" ]]; then
      tail -n 1 "${tmp}" | grep -qE '^[[:space:]]*$' || printf "\n" >>"${tmp}"
    fi
    printf "%s\n" "${RC_BLOCK_BEGIN}" >>"${tmp}"
    cat "${payload_file}" >>"${tmp}"
    printf "%s\n" "${RC_BLOCK_END}" >>"${tmp}"
  fi

  if cmp -s "${tmp}" "${rc_file}"; then
    rm -f "${tmp}" "${payload_file}"
    return 2
  fi

  _backup_file_if_exists "${rc_file}"
  cp "${tmp}" "${rc_file}"
  rm -f "${tmp}" "${payload_file}"
  return 0
}

print_path_hint() {
  local shell_kind codex_bin
  shell_kind="$(detect_shell_kind)"
  codex_bin="${HOME}/.codex/bin"

  case "${shell_kind}" in
    zsh)
      echo "[INFO] 当前 shell 未包含 ~/.codex/bin；你可以执行（临时生效）："
      echo "  export PATH=\"${codex_bin}:\$PATH\""
      echo "[INFO] 若需永久生效（zsh），建议写入 ~/.zshrc："
      echo "  export PATH=\"${codex_bin}:\$PATH\""
      ;;
    bash)
      echo "[INFO] 当前 shell 未包含 ~/.codex/bin；你可以执行（临时生效）："
      echo "  export PATH=\"${codex_bin}:\$PATH\""
      if [[ -f "${HOME}/.bashrc" ]]; then
        echo "[INFO] 若需永久生效（bash），建议写入 ~/.bashrc："
        echo "  export PATH=\"${codex_bin}:\$PATH\""
      elif [[ -f "${HOME}/.bash_profile" ]]; then
        echo "[INFO] 若需永久生效（bash），建议写入 ~/.bash_profile："
        echo "  export PATH=\"${codex_bin}:\$PATH\""
      else
        echo "[INFO] 若需永久生效（bash），建议写入 ~/.bashrc（或 ~/.bash_profile）："
        echo "  export PATH=\"${codex_bin}:\$PATH\""
      fi
      ;;
    fish)
      echo "[INFO] 当前 shell 未包含 ~/.codex/bin；你可以执行（临时生效，fish）："
      echo "  set -gx PATH \"${codex_bin}\" \$PATH"
      echo "[INFO] 若需永久生效（fish），建议执行："
      echo "  set -Ux fish_user_paths \"${codex_bin}\" \$fish_user_paths"
      ;;
    *)
      echo "[INFO] 当前 shell 未包含 ~/.codex/bin；你可以执行（临时生效）："
      echo "  export PATH=\"${codex_bin}:\$PATH\""
      echo "[INFO] 若需永久生效，请将上面这行写入你的 shell 配置文件（例如 ~/.zshrc / ~/.bashrc / ~/.profile）。"
      ;;
  esac
}

quiet="false"
ensure_rc="true"
while [[ $# -gt 0 ]]; do
  case "${1}" in
    --quiet)
      quiet="true"
      shift
      ;;
    --no-rc)
      ensure_rc="false"
      shift
      ;;
    *)
      break
      ;;
  esac
done

codex_bin="${HOME}/.codex/bin"
target="${codex_bin}/feat-wt"
skill_script="${HOME}/.codex/skills/feat-wt-kickoff/scripts/todo_sync.py"

if [[ ! -f "${skill_script}" ]]; then
  echo "[ERROR] 未找到脚本：${skill_script}" >&2
  exit 2
fi

mkdir -p "${codex_bin}"

tmp="$(mktemp)"
trap 'rm -f "${tmp}"' EXIT

cat >"${tmp}" <<EOF
#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] 未找到 python3；无法运行 feat-wt。" >&2
  exit 1
fi

script="${skill_script}"
if [[ ! -f "\${script}" ]]; then
  echo "[ERROR] 未找到 todo_sync.py：\${script}" >&2
  echo "[INFO] 可能原因：skill 未安装或路径变更。" >&2
  exit 1
fi

exec python3 "\${script}" "\$@"
EOF

should_write="true"
if [[ -f "${target}" ]]; then
  if cmp -s "${tmp}" "${target}"; then
    should_write="false"
  fi
fi

if [[ "${should_write}" == "true" ]]; then
  if [[ -f "${target}" ]]; then
    ts="$(date '+%Y%m%d-%H%M%S')"
    cp "${target}" "${target}.bak-${ts}"
    [[ "${quiet}" == "true" ]] || echo "[INFO] 已备份旧版：${target}.bak-${ts}"
  fi
  cp "${tmp}" "${target}"
fi

chmod +x "${target}"

if [[ "${quiet}" != "true" ]]; then
  echo "[OK] 已安装 feat-wt：${target}"
fi

if command -v feat-wt >/dev/null 2>&1; then
  [[ "${quiet}" == "true" ]] || echo "[OK] 当前 shell 已可用：feat-wt"
  exit 0
fi

if [[ "${ensure_rc}" == "true" ]]; then
  rc_file="$(_rc_file_for_shell)"
  payload="$(_rc_block_payload)"
  set +e
  _upsert_rc_block "${rc_file}" "${payload}"
  rc_result=$?
  set -e
  if [[ "${rc_result}" -eq 0 ]]; then
    if [[ "${quiet}" != "true" ]]; then
      echo "[OK] 已自动写入 PATH 到：${rc_file}"
      echo "[INFO] 请重新打开一个终端窗口/Tab 使配置生效。"
      echo "[INFO] 或者你可以执行（当前会话手动生效）："
      shell_kind="$(detect_shell_kind)"
      if [[ "${shell_kind}" == "fish" ]]; then
        echo "  set -gx PATH \"${codex_bin}\" \$PATH"
      else
        echo "  export PATH=\"${codex_bin}:\$PATH\""
      fi
    fi
    exit 0
  fi

  if [[ "${rc_result}" -eq 2 ]]; then
    [[ "${quiet}" == "true" ]] || echo "[OK] rc 已包含/已是最新：${rc_file}"
    exit 0
  fi

  [[ "${quiet}" == "true" ]] || echo "[INFO] 检测到 rc 中已包含 ~/.codex/bin；跳过自动写入：${rc_file}"
fi

if [[ "${quiet}" != "true" ]]; then
  print_path_hint
fi

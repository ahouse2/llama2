{
  description = "Deterministic dev shells for the llama2 workspace";

  inputs.nixpkgs = {
    type = "tarball";
    url = "https://api.flakehub.com/f/pinned/NixOS/nixpkgs/0.2505.808723+rev-b1b3291469652d5a2edb0becc4ef0246fff97a7c/0198daf7-011a-7703-95d7-57146e794342/source.tar.gz";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      uvVersion = "0.4.18";
      mkShellFor = system:
        let
          pkgs = import nixpkgs { inherit system; };
          basePackages = with pkgs; [
            python311
            poetry
            nodejs_20
            nodePackages.pnpm
            git
            just
            docker-client
            curl
          ];
          darwinDeps = if pkgs.stdenv.isDarwin then with pkgs.darwin.apple_sdk.frameworks; [ Security SystemConfiguration ] else [];
          uvBootstrap = ''
            if ! command -v uv >/dev/null 2>&1; then
              echo "[nix-shell] installing uv ${uvVersion}" >&2
              mkdir -p "$HOME/.local/bin"
              case "$(uname -s)-$(uname -m)" in
                Linux-x86_64)
                  curl -fsSL "https://github.com/astral-sh/uv/releases/download/${uvVersion}/uv-x86_64-unknown-linux-gnu.tar.gz" | tar -xz -C "$HOME/.local/bin" uv
                  ;;
                Linux-aarch64)
                  curl -fsSL "https://github.com/astral-sh/uv/releases/download/${uvVersion}/uv-aarch64-unknown-linux-musl.tar.gz" | tar -xz -C "$HOME/.local/bin" uv
                  ;;
                Darwin-arm64)
                  curl -fsSL "https://github.com/astral-sh/uv/releases/download/${uvVersion}/uv-aarch64-apple-darwin.tar.gz" | tar -xz -C "$HOME/.local/bin" uv
                  ;;
                Darwin-x86_64)
                  curl -fsSL "https://github.com/astral-sh/uv/releases/download/${uvVersion}/uv-x86_64-apple-darwin.tar.gz" | tar -xz -C "$HOME/.local/bin" uv
                  ;;
              esac
            fi
          '';
        in pkgs.mkShell {
          packages = basePackages ++ darwinDeps;
          shellHook = ''
            export POETRY_VIRTUALENVS_CREATE=false
            export UV_CACHE_DIR="${HOME}/.cache/uv"
            export PNPM_HOME="${HOME}/.local/share/pnpm"
            export PATH="${PNPM_HOME}:${HOME}/.local/bin:$PATH"
            ${uvBootstrap}
            if ! command -v pnpm >/dev/null 2>&1; then
              corepack enable pnpm >/dev/null 2>&1 || true
              corepack prepare pnpm@8.15.6 --activate >/dev/null 2>&1 || true
            fi
          '';
        };
    in {
      devShells = builtins.listToAttrs (map (system: {
        name = system;
        value = mkShellFor system;
      }) systems);
    };
}

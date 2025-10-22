import { createServer } from "http";
import { createReadStream, existsSync } from "fs";
import { promises as fs } from "fs";
import { extname, join, normalize } from "path";
import { pipeline } from "stream";
import { createGzip, createBrotliCompress } from "zlib";

const distRoot = normalize(process.env.FRONTEND_DIST_DIR ?? join(process.cwd(), "dist"));
const host = process.env.FRONTEND_HOST ?? "0.0.0.0";
const port = Number.parseInt(process.env.FRONTEND_PORT ?? "4173", 10);
const brotliPreferred = process.env.FRONTEND_ENABLE_BROTLI !== "false";

const mimeTypes = new Map([
  [".css", "text/css"],
  [".js", "application/javascript"],
  [".mjs", "application/javascript"],
  [".json", "application/json"],
  [".svg", "image/svg+xml"],
  [".png", "image/png"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".gif", "image/gif"],
  [".ico", "image/x-icon"],
  [".html", "text/html"],
  [".txt", "text/plain"],
  [".woff", "font/woff"],
  [".woff2", "font/woff2"],
]);

const compressibleExt = new Set([".html", ".css", ".js", ".mjs", ".json", ".svg", ".txt"]);

function setSecurityHeaders(res) {
  res.setHeader("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'");
  res.setHeader("Referrer-Policy", "strict-origin-when-cross-origin");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("X-XSS-Protection", "1; mode=block");
  res.setHeader("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload");
}

async function resolveAssetPath(urlPath) {
  const decoded = decodeURIComponent(urlPath.split("?")[0].split("#")[0]);
  let candidate = normalize(join(distRoot, decoded));

  if (!candidate.startsWith(distRoot)) {
    return null;
  }

  try {
    const stats = await fs.stat(candidate);
    if (stats.isDirectory()) {
      const indexFile = join(candidate, "index.html");
      return existsSync(indexFile) ? indexFile : null;
    }
    return candidate;
  } catch {
    const fallback = join(distRoot, "index.html");
    return existsSync(fallback) ? fallback : null;
  }
}

const server = createServer(async (req, res) => {
  if (!req.url) {
    res.statusCode = 400;
    res.end("Bad Request");
    return;
  }

  if (req.url === "/health") {
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ status: "ok", service: "frontend" }));
    return;
  }

  const assetPath = await resolveAssetPath(req.url);
  if (!assetPath) {
    res.statusCode = 404;
    res.end("Not Found");
    return;
  }

  const ext = extname(assetPath);
  const mimeType = mimeTypes.get(ext) ?? "application/octet-stream";

  setSecurityHeaders(res);
  res.setHeader("Content-Type", mimeType);
  res.setHeader("Cache-Control", ext === ".html" ? "no-cache" : "public, max-age=31536000, immutable");

  const acceptEncoding = req.headers["accept-encoding"] ?? "";
  const supportsBrotli = brotliPreferred && acceptEncoding.includes("br");
  const supportsGzip = acceptEncoding.includes("gzip");
  const shouldCompress = compressibleExt.has(ext);

  const stream = createReadStream(assetPath);
  if (shouldCompress && (supportsBrotli || supportsGzip)) {
    if (supportsBrotli) {
      res.setHeader("Content-Encoding", "br");
      pipeline(stream, createBrotliCompress(), res, (err) => {
        if (err) {
          console.error("Brotli pipeline error", err);
        }
      });
    } else {
      res.setHeader("Content-Encoding", "gzip");
      pipeline(stream, createGzip({ level: 6 }), res, (err) => {
        if (err) {
          console.error("Gzip pipeline error", err);
        }
      });
    }
    return;
  }

  pipeline(stream, res, (err) => {
    if (err) {
      console.error("Stream pipeline error", err);
    }
  });
});

server.listen(port, host, () => {
  console.log(`discovery-frontend listening on http://${host}:${port}`);
});

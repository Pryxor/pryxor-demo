"""smtp_sink.py — a minimal, dependency-free SMTP server that stores every
incoming email as a .eml file in MAILDIR. Lets the demo send *real* email
without any external service, so blocked/held sends are fully observable.
"""
import os, time, socketserver

MAILDIR = os.environ.get("MAILDIR", "./mail")
os.makedirs(MAILDIR, exist_ok=True)

class SMTPSink(socketserver.StreamRequestHandler):
    def push(self, msg):
        self.wfile.write((msg + "\r\n").encode())
        self.wfile.flush()

    def handle(self):
        self.push("220 mailpryxor ESMTP ready")
        mail_from, rcpts, data_mode, lines = None, [], False, []
        while True:
            raw = self.rfile.readline()
            if not raw:
                return
            line = raw.decode("utf-8", "replace").rstrip("\r\n")
            if data_mode:
                if line == ".":
                    data_mode = False
                    name = f"{int(time.time() * 1000)}_{len(rcpts)}.eml"
                    path = os.path.join(MAILDIR, name)
                    with open(path, "w") as f:
                        f.write(f"From: {mail_from}\nTo: {', '.join(rcpts)}\n\n")
                        f.write("\n".join(lines))
                    print(f"[sink] stored {name}  from={mail_from}  to={rcpts}", flush=True)
                    lines = []
                    self.push("250 2.0.0 OK queued")
                else:
                    lines.append(line[1:] if line.startswith(".") else line)
                continue
            verb = line.split(":", 1)[0].split(" ", 1)[0].upper()
            if verb in ("HELO", "EHLO"):
                self.push("250 mailpryxor greets you")
            elif verb == "MAIL":
                mail_from = line.split(":", 1)[1].strip()
                self.push("250 2.1.0 OK")
            elif verb == "RCPT":
                rcpts.append(line.split(":", 1)[1].strip())
                self.push("250 2.1.5 OK")
            elif verb == "DATA":
                data_mode = True
                self.push("354 End data with <CR><LF>.<CR><LF>")
            elif verb == "RSET":
                mail_from, rcpts = None, []
                self.push("250 2.0.0 OK")
            elif verb == "NOOP":
                self.push("250 2.0.0 OK")
            elif verb == "QUIT":
                self.push("221 2.0.0 Bye")
                return
            else:
                self.push("250 2.0.0 OK")  # lenient: accept and log

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "1025"))
    print(f"[sink] listening on 0.0.0.0:{port} -> {MAILDIR}", flush=True)
    Server(("0.0.0.0", port), SMTPSink).serve_forever()

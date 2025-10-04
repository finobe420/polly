# Polly
Polly is a relatively simple [Gopher](https://en.wikipedia.org/wiki/Gopher_(protocol)) server written in Python 3.12. No external dependencies are required.

# POLscript
POLscript is like a raw Gophermap file with shell command execution built-in. If a line is prefixed with `\EXC`, then it will run a command intertwined with the regular Gophermap.

# POLscript example
[tab] = tab character
```
iI'm just a regular Gophermap, living life as static plain-text.[tab]err[tab]host.err[tab]0
i...Just kidding, here's a figlet.[tab]err[tab]host.err[tab]0
\EXCi[tab]figlet -f lean awesome figlet[tab]err[tab]host.err[tab]0
iDid you like my figlet? No? Fuck you, then![tab]err[tab]host.err[tab]0
```

cat in.txt | tr -cs A-Za-z0-9 '\n' | sort | uniq -c | sort -rn | head -5

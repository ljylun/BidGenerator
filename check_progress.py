import os, glob
folder = r"h:\DEV\MyProjects\BidGenerator\doc\技术标"
files = sorted(glob.glob(os.path.join(folder, "*.md")))
total = 0
for f in files:
    size = os.path.getsize(f)
    total += size
    name = os.path.basename(f)
    print(f"{name:<35} {size:>10,} bytes")
print("-" * 50)
print(f"{'TOTAL':<35} {total:>10,} bytes")

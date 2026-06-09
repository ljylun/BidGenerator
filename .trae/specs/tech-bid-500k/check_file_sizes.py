import os
import glob

folder = r"h:\DEV\MyProjects\BidGenerator\doc\技术标"
files = sorted(glob.glob(os.path.join(folder, "*.md")))
total = 0
print(f"{'文件名':<35} {'字节数':>10} {'估算中文字数':>12}")
print("-" * 60)
for f in files:
    size = os.path.getsize(f)
    total += size
    name = os.path.basename(f)
    print(f"{name:<35} {size:>10,} {size//2:>10,}")
print("-" * 60)
print(f"{'总计':<35} {total:>10,} {total//2:>10,}")

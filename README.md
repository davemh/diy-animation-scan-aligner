# diy-animation-scan-aligner
Batch scan auto-alignment tool for animators working on paper, using a round pegbar and 3-hole punch.

<h2>About</h2>
DIY Animation Scan Aligner is an auto-alignment tool for animators who work on paper and use a standard 3-hole punch and pegbar with round pegs, rather than ACME. It is meant to address a gap in available tools for auto-alignment of scanned drawings on paper -- none of which were designed with standard 3-hole punch in mind.

<h2>Usage</h2>
<p>For now, this is a command-line tool. In its current state, Scan Aligner assumes you animated on top pegs. It looks for scans in the **scans/** subdirectory, and outputs to the **aligned/** subdirectory.</p>
<p>To run it on MacOS, use the following commands:</p>

# To align scans of pages animated on top pegs (Japan industry standard)
python3 align_pages.py scans/ aligned/

# To align scans of pages animated on bottom pegs (more common amongst US animation students)
python3 align_pages.py scans/ aligned/ --holes-position bottom

# Display debug overlay
python3 align_pages.py scans/ aligned/ --debug

# Auto-play preview of alignment process, 0.5s per page
python3 align_pages.py scans/ aligned/ --preview

# Auto-play preview of alignment process, 1s per page, showing file name & progress
python3 align_pages.py scans/ aligned/ --preview --preview-delay 1000
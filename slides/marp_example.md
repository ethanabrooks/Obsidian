---
marp: true
# theme: gaia  # Removed custom theme, will use default
size: 16:9
paginate: true # Page numbers are usually fine
html: true # Enable HTML tags explicitly
---

# Slide 1: Introduction

This slide uses standard heading and paragraph styles.

Marp makes presentations easy!

---

# Slide 2: Details

Here we have more details on the second slide.

- Detail X
- Detail Y
- Detail Z

<!--
Speaker notes:
- Remember to mention the Q3 results here.
- Highlight the synergy between X and Y.
-->
<!-- Speaker notes generally don't interfere with visual import -->

---

# Slide 3: Images (Simplified)

You can include images using standard Markdown:

![](https://napaliexperience.com/wp-content/uploads/sites/3579/2020/03/Screen-Shot-2020-03-19-at-2.51.55-AM.png?w=600&zoom=2)

This text will appear below the image (or wherever standard Markdown flow places it). We removed the `bg right:40%` syntax which relies on complex CSS positioning.

---

# Slide 4: Code Block Test (HTML)

Let's see how a code block translates using HTML tags:

<pre><code class="language-python">import sys

def main(args: list[str]):
    """A simple main function."""
    if not args:
        print("Usage: script.py &lt;name&gt;") # Escaped '<'
        sys.exit(1)
    print(f"Hello, {args[0]}!")

if __name__ == "__main__":
    main(sys.argv[1:])
</code></pre>

Check if this code block translates better regarding the font when using HTML tags.

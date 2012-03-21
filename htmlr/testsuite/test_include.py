import unittest
from htmlr import *
from htmlr.include import markdown

class TestInclude(unittest.TestCase):

    def gen(self, n, p=True):
        c = n.compile()
        nr = n.render()
        cr = c.render()
        if p:
            print(n.display())
            print(c.display())
            print(nr)
            print(cr)
        return c, nr, cr

    def test_markdown(self):
        n = doctype.html(body(markdown("test.md")))
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "!DOCTYPE {} []\n"
                                      "html {} []\n"
                                      "    body {} []\n"
                                      "        $markdown: test.md\n")
        self.assertEqual(c.display(),
"""*str <!DOCTYPE html><html><body><h1 id="this-is-a-test">This Is A Test</h1>
<p>This is to test the markdown extension.</p>
<div class="codehilite"><pre><span class="n">def</span> <span class="n">go</span><span class="p">():</span>
    <span class="n">pass</span>
</pre></div>


<p>Hopefully this works!</p>
<ul>
<li>It would be nice</li>
<li>and plesant</li>
</ul>
<p>That is all</p></body></html> [] {}\n""")
        self.assertEqual(nr,
"""<!DOCTYPE html><html><body><h1 id="this-is-a-test">This Is A Test</h1>
<p>This is to test the markdown extension.</p>
<div class="codehilite"><pre><span class="n">def</span> <span class="n">go</span><span class="p">():</span>
    <span class="n">pass</span>
</pre></div>


<p>Hopefully this works!</p>
<ul>
<li>It would be nice</li>
<li>and plesant</li>
</ul>
<p>That is all</p></body></html>""")
        self.assertEqual(cr,
"""<!DOCTYPE html><html><body><h1 id="this-is-a-test">This Is A Test</h1>
<p>This is to test the markdown extension.</p>
<div class="codehilite"><pre><span class="n">def</span> <span class="n">go</span><span class="p">():</span>
    <span class="n">pass</span>
</pre></div>


<p>Hopefully this works!</p>
<ul>
<li>It would be nice</li>
<li>and plesant</li>
</ul>
<p>That is all</p></body></html>""")

if __name__ == "__main__":
    unittest.main()

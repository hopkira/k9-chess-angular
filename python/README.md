## Installation steps ##
1. By default Raspberry Pi does come with Python 2.7.5 installation. In case its not installed, first install it.
2. Run the simulator
  <pre><code>python node_RED_harness.py localhost</code></pre>
3. If the above command throws library error, install the library
  <pre><code>pip install ws4py</code></pre>
4. In case pip did not install the library properly carry out the following steps
  1. Check for the pip version, if its not the latest, download it
     <pre><code>wget https://bootstrap.pypa.io/get-pip.py</code></pre>
  2. Install the latest version of pip that you downloaded
     <pre><code>sudo python2.7 get-pip.py</code></pre> 
  3. Install the ws4py library
     <pre><code>sudo pip2.7 install ws4py</code</pre>

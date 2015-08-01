
YamlWeb
==============

Web development is hard. You have to learn at least three languages to create
an application that would take one on other platforms.

If I could get in a time machine and go back to the dawn of the web
(and not try to reinvent everything)
I'd probably try to implement something like a subset of YAML instead, perhaps
with Python for scripting. (I might also like to separate documents from
applications but that is a subject for another day.)

"Transpilers" and new languages are all the rage these days,
so what's one more??
This is an *experiment* to see if YAML is usable for web markup and styles.

The included scripts convert YAML that looks like bare HTML or CSS and
converts them to the real thing!  This is similar to Haml & SASS/but without a
custom language and ruby dependency.

Also thought about implementing a "yaml version of javascript" at some point
but there is obviously a large mismatch to overcome.
Nice things like coffeescript, typescript, pyjs, and brython already exist,
however.
I recommend those as companions, see
https://github.com/jashkenas/coffeescript/wiki/list-of-languages-that-compile-to-js
for a nice list.


Issues
------------

There are still a few awkward issues to address in the conversion,
though I've already squashed the majority.
For example, I've had to deactivate a few of the features of YAML/PyYAML such
as flow syntax and directives.
One remaining problem,
is that the "#" character has to be quoted if it starts a line in a css
selector.

I'm hoping to solve those by overriding classes in PyYAML and ElementTree,
but if it doesn't work or is too difficult,
a custom parser should allow a conversion with zero annoyances or
edge-cases.


html in yaml
--------------

Let's get to it shall we?
This is what a page looks like,
mapping keys ending in colons start block elements,
with attributes given just after the "tag" name.

.. code:: yaml

    html lang=en:  # optional, perhaps you'd like to set lang

        head:
            title: Amazing Title
            meta varname=value:     # note - this will be changed to std form
            link rel=stylesheet href=style.css type=text/css media=screen:
            link rel=stylesheet href="http://fonts.googleapis.com/css?family=Open+Sans":
            style:  # same syntax for styles:
                body:
                    padding: 2em

            # accepts common templating syntax:
            script src="{{ static_dir }}/scripts/foo.js":
            script deferred: |  # this pipe char keeps formatting in yaml

                // hello world

        body:
            header class="one two":
                h1#main:
                    Profile for {{ username }}
        ...

Which will convert to this HTML:

.. code:: html

    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Amazing Title</title>
            <meta content="value" name="varname">
            <link href="style.css" media="screen" rel="stylesheet" type="text/css">
            <link href="http://fonts.googleapis.com/css?family=Open+Sans" rel="stylesheet" type="text/css">
            <style>
            body {
                padding: 2em;
            }
            </style>
            <script src="{{ static_dir }}/scripts/foo.js"></script>
            <script deferred="deferred">
            // hello world
            </script>
        </head>
        <body>
            <header class="msg bold">
                <h1 id="main">Profile for {{ username }} II</h1>
            </header>

        ...

One issue I'm still thinking about is what to do with "inline" markup.
What I mean by this is,
it's easy enough to model the block tags with yaml maps
(aka dict/hash/assoc arrays).
But, what happens when you you'd like a run of html with/without block
containers?

.. code:: html

    This text represents a blog post.<br> Line two is here.<img src=...><br>
    <span class="highlight">Line three.</span><br>

For now I've decided to use a list of text fragments
(with mapping keys when tags are needed, note the trailing colons):

.. code:: yaml

    article:
            - span class=warning:
                Warning Text!
            - br:
            - So this is going to be some text with markup interspersed.
            - p:
                {{ post }}
            - b:
                How to do that, exactly?
            - br:
            # below a complex key, allows one to split a long line into several
            - ?
                img src="{{ static_dir }}/images/foo.jpg"
                title="a very nice image"
                height=180 width=240 align=middle  # tsk, tsk but possible
              : img is not a container in html, so text appears after.
            - br:

If there is a better way to do this I'd like to hear it,
pls file an enhancement issue.


css in yaml
------------

While:

.. code:: yaml

    vars:                # how to use variables
        bgcolor: window  # system colors
        fgcolor: 221818

    # the first colon below may not have whitespace after it,
    # or must be quoted
    @media (max-width:600px):
        .facet_sidebar:
            display: none

    @font-face:
        font-family: cool_font
        src: url('cool_font.ttf')


    *, *:before, *:after:
        box-sizing: border-box

    body:
        margin: 1em
        padding: 2em
        height: 50em
        # nums of 3,6 chars will be converted to hex:
        color: {fgcolor}
        # bg is shortcut for background, bgcolor is a variable defined above:
        bg: {bgcolor}
        border: 1px solid 888   # same here
        border-radius: .5em
        font-family: "'Open Sans', sans-serif"  # need to escape quotes

    # "#" char can be used inside a word, but not begin a word
    body h1#main, h2:
        border-bottom: 1px dotted 222
    "#main, h2":  # this form must be quoted
        color: 264 !important

    ...

Will convert to this:

.. code:: css

    @charset: "utf-8";

    @media (max-width:600px) {
        .facet_sidebar {
            display: none;
        }
    }

    @font-face {
        font-family: cool_font;
        src: url('cool_font.ttf');
    }

    *, *:before, *:after {
        box-sizing: border-box;
    }

    body {
        margin: 1em;
        padding: 2em;
        height: 50em;
        color: #221818;
        background: window;
        border: 1px solid #888;
        border-radius: .5em;
        font-family: 'Open Sans', sans-serif;
    }

    body h1#main, h2 {
        border-bottom: 1px dotted #222;
    }

    #main, h2 {
        color: #264 !important;
    }
    ...

Still need to implement prefixing for CSS but it should be easy.


Install
------------

Should work under Python 2.x and 3.x.

.. code:: bash

    # download, unpack, run setup.py
    cd folder
    setup.py install   # might need sudo

or

This is not available yet, but will be if a few requests are made::

    sudo pip install yamlweb



Use
------------

.. code:: bash

    yaml2html page.yaml -O -i 4  # outputs to page.html, indents 4 spaces

    yaml2css style.yaml -O -i 4  # outputs to style.css, indents 4 spaces

    # or from stdin
    cat page.yaml | yaml2html > page.html


Todo
------------

- Add markdown and/or rst support.
- Sort CSS rules, not selectors.


License
------------

GNU GPL 3+


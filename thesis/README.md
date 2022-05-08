# Latex setup used for thesis writing (Latex, VS Code, draw.io and GitHub)

## What is this about?
This project was started as part of a further education course which included
writing a thesis. Here I am outlining the setup I used to write the thesis found
in this folder using Latex, VS Code, draw.io and GitHub. It is a setup that is
completely free, provides convenience features like real-time compilation of
your Latex documents to PDF and uses version control, so you never ever lose
your work.

## How it changed my perspective on thesis writing
This repository was started as part of a GIS further education program which
included writing a thesis. I've written my last thesis years ago as part of my
Master's program in Word, and it was frankly a horrible experience. To be fair,
the main reason was probably my inadequate knowledge of the advanced concepts of
Word, but it does not change the fact that thinking about ever writing another
thesis sends chills down my spine to this day.

As a voluntary secondary take-away from this further education I wanted to give
thesis writing another try using Latex, which the cool kids during my studies
always talked about, but I never got around to learn.

I am happy to say that this was one of the best decisions ever and that I feel
for the first time that I have found a setup that works for me to write
documents in a fun way that I feel would scale to almost arbitrary complexity.
To that end I want to share my setup here in the hope to enable somebody to have
a similar experience.

## Setup
1. Download and install a basic TeX/LaTeX engine on your machine. [TeX
   Live](https://www.tug.org/texlive/) is recommended. An alternative is
   [MiKTeX](https://miktex.org/download) which requires you to install Perl as
   an extra dependency for further steps if not already available.
2. Install [Visual Studio Code (VS Code)](https://code.visualstudio.com/), an
   extremely powerful and extensible editor I use for almost all my programming
   and writing tasks.
3. In VS Code, install the extension [LaTeX
   Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop),
   which will give you real-time compilation of your documents and the ability
   to show a continuously updated PDF preview in a side window.
4. In VS Code, install the extension [LTeX – LanguageTool grammar/spell
   checking](https://marketplace.visualstudio.com/items?itemName=valentjn.vscode-ltex),
   which will give you spell checking and wording suggestions.
5. In VS Code, install the extension
   [draw.io](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio),
   which will give you the possibility to use draw.io directly in VS Code to
   draw and export diagrams.
6. Create a GitHub account if necessary, create a new repository for your
   document and [link it to VS
   Code](https://code.visualstudio.com/docs/editor/github).
7. You should now be able to write Latex documents in VS Code with spell
   checking, live compilation and an easy way to create and integrate diagrams.
   Whenever you are done writing a section, stage your changes, push them to
   your GitHub repository and enjoy the feeling that your computer could explode
   right now and all your work is saved in GitHub's version control cloud.

## Why not Overleaf?
To be fair, I did not give [Overleaf](https://www.overleaf.com/) more than a few
minutes of my time after I found out that I had to pay a monthly fee for
features I consider a core necessity like integration with version control. From
my brief research Overleaf looks amazing when it comes to real-time
collaborative work, which is definitely the great free feature they use to hook
customers and provide an incentive to pay for other more basic features. I
currently have no need for real-time collaboration on my Latex documents and
even if I will ever collaborate I will probably prefer the classic version
controlled way via commits and pull requests. Hence, what Overleaf provides I do
not need and what I need, I get with the setup above without monthly
subscription.

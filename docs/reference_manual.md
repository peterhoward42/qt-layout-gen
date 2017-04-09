# Concise Reference Manual

## Three Input Variations
    my_box:QVBoxLayout          child_a     child_b     ... # Canonical form
    my_box:VBOX                 child_a     child_b     ... # Shortcut form
    my_thing:Find:CustomClass   child_a     child_b     ... # 'Find' form

## Behaviour
The *canonical* form example instantiates a QVBoxLayout, which it then refers to 
as *my_box*, and adds *child_a* and *child_b* to it as children.

The *shortcut* form provides shortcut keywords that can be used in place of 
*QWidget* or *QLayout* class names from the set:

    VBOX | HBOX | STACK | SPLIT | TAB
    
The *Find* form example does not instantiate an object, but instead introspects 
your running program to find an object of type *CustomClass* that you have
**already** instantiated, and which you referred to with a variable named 
*my_thing*, or an attribute named *my_thing*. For example:

    my_thing = CustomClass()
    foo.my_thing = CustomClass()

## Parsing Contract
Spaces, tabs and newline characters are all treated equally - as whitespace.
The input is split at whitespace into *words*. Words are bunched into 
*records* which start at a word with one or two colons in and which end with 
the word that precedes the next *colon word* (or EOF).

A hash introduces a comment, which extends to the end of the line.

    # I am a comment
    my_box:QVBoxLayout child_a child_b # So am I
    
Comments are removed (conceptually) before the rest of the parsing contract 
is applied. From which it follows that a record may span multiple lines.

## Parent types
We refer to the *colon word* as the *Left Hand Side* (LHS). The LHS always 
defines an object derived from QWidget or QLayout, and creates a named object 
that can then be used as a child name on some other RHS.

Names need not be defined *before* they are used, provided they are defined 
somewhere in the input.

## How Children are Added to Parents
When a child name resolves to a parent object that is defined somewhere else 
in the input, the system tries the following method calls on the parent object
in order (regardless of the parent / child types), and stops as soon as one of 
them works:

    addLayout(child)
    setLayout(child)
    addWidget(child)
    addTab(child)
    
This procedure allows:
*  Layout children to be added to layout parents
*  The layout to be set for a widget.
*  Widgets to be added to a QStackedWidget
*  Widgets to be added to a QTabbedWidget
*  Arbitrary child addition to custom classes that implement one of the 
   methods.
   
## Adding Text To Labels, Buttons, GroupBoxes Etc.
When a child name does not resolve to a known parent, the system treats the
child name as a string that should be be used in a

    setText(child name)
    
method call on the parent object. It replaces double underscores present in the
child name with a space, so that:
    
    my_label:QLabel Hello__World
    
Produces a QLabel with the text 'Hello World'

## Three Ways To Provide the Input Text

    build_layouts_from_text(one big string)
    build_layouts_from_file(file path)
    build_layouts_from_directory(directory path) # All files recursively.
    
## The LayoutsCreated Object
The functions above all return a **LayoutsCreated** object. 
Every named artefact defined by the input (and thus every node in 
the layout tree(s)), is available as:

    layout_created.layout_element(name)
    
Which implies that the names used in the input must be unique to to 
the scope of any one *build_layouts_from_xxx()* call.
    
The layouts need not resolve to a single tree with a single root.
I.e. they can include layout fragments.

For diagnostic purposes, the system's model of the hierarchies 
created is available (in a tree-like textual format) from:

    layout_created.dump_tree()

## Reserved Child Names
The system reserves the child name *'<>'* to signify the addition 
of a stretch item to a QBoxLayout.

    my_box:HBOX foo bar <> baz
    
In this case the *foo* and *bar* items will be pushed to the left, 
of the QHBoxLayout, while the *baz* item will be pushed to the 
right.

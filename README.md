# Behavior Tree

A behavior tree algorithm for a Roomba vacuum that makes decisions based on
the environment and its internal state. bt.py uses a hierarchy of nodes to
represent the behavior tree specified in `BT.pdf`. The behavior tree
directs a Roomba vacuum to perform spot cleaning, general cleaning, both,
or do nothing.

## Running the Script

Run the script using `python ./bt.py`. Use `^C` to stop the script.

## Debug Mode

To print out the status of each node each time the BT is run, use the flags
`-v` or `--verbose`. To clarify the naming of each node: 

- `timer1`: Timer for `clean spot` in general cleaning
- `timer2`: Timer for `clean spot` in spot cleaning
- `seq1`: Sequence for `dusty spot` and `timer1`
- `sel1`: Selector for `seq1` and `clean`
- `neg1`: Negation for `Battery < 30%` in general cleaning
- `seq2`: Sequence for `neg1` and `sel1`
- `seq3`: Sequence for the `until success` node and `done general`

## Structure

Each type of node (`Task`, `Condition`, `Composite`, etc.) is represented
as a class that inherits from the `Node` class, which contains a node's
`name`, `children`, and `status`. Each of these node classes could inherit
themselves to another class that performs a more specific function (i.e.
`Sequence`, `Selector`, and `Priority` inherits from `Composite`). Each
type of node contains a `run` function that executes its function. The tree
is then built by creating each node and adding a given node's children to
its `children` element.

The tree is then run from the root, which propagates down until the lowest
level. If a node is running (when a timer is used), the BT stops iterating
through the tree and rerun from the root, and deduces a second from the
timer until the task is completed.

When the battery of the Roomba falls below 30%, it performs a charging
sequence and docks itself. The Roomba will not undock until it has 100%
battery. 

In my interpretation of the BT, it is impossible to reach `done general`.
The robot will do general cleaning until it reaches 30%, recharge, continue
to clean until 30%, and repeat (that is, the `until_success` node 
will never have a status of `SUCCESS`, since either `neg1` will fail, or
`clean` will be running, and `until_success` requires both to be `SUCCESS`
in order to become `SUCCEED`).

## Future Improvements

Currently, the charging sequence is run within one evaluation of the
behavior tree. This creates the illusion that all three steps of the
sequence (find home, go home, dock) are being done within one step. The
goal is to fix this and perform only one task each time the BT is run.

## References

- https://www.pirobot.org/blog/0030/
- TAs

## Author

Jiayi (Frank) Ma

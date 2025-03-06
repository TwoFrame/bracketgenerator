## Requirements

[Node.js + npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

## Description


Run `node install` then`npm run dev`, then visit `localhost:3000`.
This is a simple site that displays double elimination brackets using [reactflow](https://reactflow.dev/)

`bracket_generator.py` is the script for generating the nodes, and edges for an N sized bracket, where 2 <= N <= 128.
`python3 bracket_generator.py` generates the file **SerializedBrackets.json**, which is what the site uses to display brackets.
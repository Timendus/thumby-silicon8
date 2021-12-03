#!/usr/bin/env node

const fs   = require('fs');
const file = process.argv[2];

// Read file as binary array
const bytes = new Uint8Array(
                Buffer.from(
                  fs.readFileSync(file, 'binary'),
                  'binary'
                )
              );

// Chunk array into lines of  30 items per line
const chunkSize = 30;
const lines = bytes.reduce((a, v, i) => {
  const index = Math.floor(i/chunkSize);
  a[index] ||= [];
  a[index].push(v);
  return a;
}, []);

// Output as MicroPython tuples
console.log(`
program = (
  ${lines.map(bytes =>
      bytes.map(byte =>
        '0x' + byte.toString(16)
                .padStart(2, '0')
      ).join(', ')
    ).join(',\n  ')}
)
`);

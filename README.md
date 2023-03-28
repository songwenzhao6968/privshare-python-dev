# Privshare Python Dev
## Requirements
+ Python 3.9
+ Pyfhel 3.4.1
## Usage
Directly run `main.py`.
## Micro-benchmark
<table>
    <thead>
        <tr>
            <th colspan=2 style="text-align: center">Operation</th>
            <th style="width:30%">Amortized running time per record (µs)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan=6 style="text-align: center">HE</td>
            <td>Plaintext add</td>
            <td>0.13</td>
        </tr>
        <tr>
            <td>Ciphertext add</td>
            <td>0.10</td>
        </tr>
        <tr>
            <td>Plaintext mul</td>
            <td>0.04</td>
        </tr>
        <tr>
            <td>Ciphertext mul</td>
            <td>4.84</td>
        </tr>
        <tr>
            <td>Rotation</td>
            <td>1.81</td>
        </tr>
        <tr>
            <td>Relinearization</td>
            <td>1.78</td>
        </tr>
        <tr>
            <td rowspan=4 style="text-align: center">Building Block</td>
            <td>8-bit elementwise mapping</td>
            <td>664.29</td>
        </tr>
        <tr>
            <td>Boolean - NOT</td>
            <td>0.09</td>
        </tr>
        <tr>
            <td>Boolean - AND</td>
            <td>6.21</td>
        </tr>
        <tr>
            <td>Boolean - OR</td>
            <td>6.25</td>
        </tr>
        <tr>
            <td rowspan=4 style="text-align: center">Composition</td>
            <td>16-bit equality check</td>
            <td>664.29</td>
        </tr>
        <tr>
            <td>16-bit range query (single side)</td>
            <td>664.29</td>
        </tr>
        <tr>
            <td>16-bit range query (single side)</td>
            <td>664.29</td>
        </tr>
    </tbody>
</table>
|# 📦 UART Packet Structure Documentation

This document provides a detailed analysis of a custom UART protocol that uses a 28-byte packet format for communication. The protocol appears to follow a structured layout with fixed headers, a variable data field, and fixed terminators.

---

## 🔧 Packet Overview

- **Standard Packet Size:** 28 bytes  
- **Packet Type:** Fixed-header, single-data-byte, fixed-terminator  
- **Purpose:** Request-response or state reporting with optional single-byte control packets

---

## 🧱 Packet Structure (28 Bytes)

| **Byte Position** | **Value** | **Description**       | **Type**   |
|-------------------|-----------|------------------------|------------|
| 1                 | `0x30`    | Header byte 1          | Fixed      |
| 2                 | `0x36`    | Header byte 2          | Fixed      |
| 3                 | `0x26`    | Header byte 3          | Fixed      |
| 4                 | `0x00`    | Header byte 4          | Fixed      |
| 5                 | `0x0C`    | Header byte 5          | Fixed      |
| 6                 | `0x30`    | Header byte 6          | Fixed      |
| 7                 | `0x40`    | Header byte 7          | Fixed      |
| 8                 | `0x00`    | Header byte 8          | Fixed      |
| 9                 | `0xFC`    | Header byte 9          | Fixed      |
| 10                | `0x30`    | Header byte 10         | Fixed      |
| 11                | `0x00`    | Header byte 11         | Fixed      |
| 12                | `0x30`    | Header byte 12         | Fixed      |
| 13                | `0x42`    | Header byte 13         | Fixed      |
| 14                | `0x00`    | Header byte 14         | Fixed      |
| 15                | `0x32`    | Header byte 15         | Fixed      |
| 16                | `0x30`    | Header byte 16         | Fixed      |
| 17                | `0x00`    | Header byte 17         | Fixed      |
| 18                | `0x30`    | Header byte 18         | Fixed      |
| 19                | `0x82`    | Header byte 19         | Fixed      |
| 20                | `0x40`    | Header byte 20         | Fixed      |
| 21                | `0x00`    | Header byte 21         | Fixed      |
| 22                | `0x30`    | Header byte 22         | Fixed      |
| 23                | `0x0E`    | Header byte 23         | Fixed      |
| 24                | `0x00`    | Header byte 24         | Fixed      |
| 25                | `0x00`    | Header byte 25         | Fixed      |
| 26                | *Varies*  | **Data byte**          | Variable   |
| 27                | `0xCE`    | Terminator 1           | Fixed      |
| 28                | `0xFE`    | Terminator 2 / Status? | Fixed/Semi |

---

## 🔁 Variable Byte (Position 26)

This is the **only dynamic byte** in the standard packet. It likely encodes sensor data, state changes, or control signals.

### Observed Values and Frequency

| **Value** | **Frequency** | **Interpretation**     |
|-----------|----------------|-------------------------|
| `0x30`    | ~80%           | Normal state            |
| `0x32`    | ~15%           | Alternate state         |
| `0xF0`    | ~3%            | Occasional variation    |
| `0xFE`    | ~1%            | Rare variation          |
| `0xFF`    | ~1%            | Possible error indicator|

---

## 🔚 Terminator Bytes

- **Byte 27 (`0xCE`)** and **Byte 28 (`0xFE`)** serve as fixed terminators.
- Byte 28 occasionally changes to `0xFF`, suggesting it may also act as a **status flag** (e.g., error reporting).
- **Not a checksum byte.** Byte 28 behaves more like a protocol marker.

---

## 🚗 Gear Position Encoding

**IMPORTANT:** Analysis of gear shifting vs idle datasets reveals specific byte patterns that correlate with gear position.

### Primary Gear Indicators

#### 1. Terminator Pattern (Bytes 27-28) - **Most Reliable**

| **Gear** | **Terminator Pattern** | **Description** |
|----------|----------------------|-----------------|
| **1**    | `0x8c`              | Incomplete terminator (missing 0xfe) |
| **2**    | `0x4c 0xfe`         | Partial terminator |
| **3**    | `0xce 0xfe`         | Complete standard terminator |

**Key Observation:** The **terminator progression** `0x8c` → `0x4c 0xfe` → `0xce 0xfe` directly correlates with gear position.

#### 2. Data Byte Changes (Byte 26) - **Direct Correlation**

| **Gear** | **Data Byte Value** | **Hex Value** |
|----------|-------------------|---------------|
| **1**    | `0x8c`           | 140 (Gear 1 indicator) |
| **2**    | `0x4c`           | 76 (Gear 2 indicator) |
| **3**    | `0xce`           | 206 (Gear 3 indicator) |

**Pattern:** The **third-to-last byte** changes from `0x8c` → `0x4c` → `0xce` as gears progress.

#### 3. Header Variations (Byte 3) - **Less Consistent**

| **Gear** | **Header Byte 3** | **Frequency** |
|----------|------------------|---------------|
| **1**    | `0x26`          | Standard header |
| **2-3**  | `0x26`/`0x36`   | Modified header (occasional) |

### Gear Position Encoding Summary

| **Gear** | **Terminator** | **Data Byte (26)** | **Header Byte (3)** |
|----------|----------------|-------------------|-------------------|
| **1**    | `0x8c`        | `0x8c`           | `0x26`           |
| **2**    | `0x4c 0xfe`   | `0x4c`           | `0x26`/`0x36`    |
| **3**    | `0xce 0xfe`   | `0xce`           | `0x26`/`0x36`    |

### Control Byte Frequency During Shifting

- **High `0x02` frequency:** ~50 occurrences during gear shifts (acknowledgments)
- **`0xFF` occurrences:** Error indicators during shift transitions
- **Dynamic control pattern:** Varies with shifting activity vs static idle state

---

## 📏 Packet Size Distribution

| **Size (bytes)** | **Frequency** | **Purpose**               |
|------------------|----------------|----------------------------|
| 28               | ~80%           | Standard data packet       |
| 1                | ~15%           | Control/ACK/status byte    |
| 8–15             | ~3%            | Short/partial data packet  |
| 20–25            | ~2%            | Truncated packets          |

---

## 🔘 Common Single-Byte Control Packets

These appear between standard packets and may represent protocol commands or acknowledgments.

| **Value** | **Frequency** | **Likely Meaning**     |
|-----------|----------------|-------------------------|
| `0x02`    | ~60%           | Acknowledgment (ACK)    |
| `0xFE`    | ~20%           | Status update           |
| `0xFF`    | ~10%           | Error indicator         |
| `0x00`    | ~5%            | Null/empty              |
| `0x01`    | ~3%            | Control signal          |
| `0xFC`    | ~2%            | Flow control            |

---

## ✅ Summary

- The protocol uses **fixed 25-byte headers**, 1-byte variable data, and 2-byte terminators.
- **No checksum byte** is currently present.
- Protocol includes **single-byte packets** for control and acknowledgment.
- **Byte 26** carries variable payload data.
- **Byte 28** acts as a terminator and may signal error conditions (`0xFF`).
- **Gear position is encoded primarily in terminator bytes** with clear progression patterns.
- **Data byte 26** shows direct correlation with gear position (`0x8c` → `0x4c` → `0xce`).

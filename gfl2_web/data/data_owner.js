/**
 * Owner definitions.
 * @type {[ownerId: number, ownerTag: string, startDate: string][]}
 */
const DATA_OWNER = [
  [1, "GM", "2025-03-16"],
  [2, "IB", "2025-03-28"],
  [3, "FB", "2025-04-17"],
];

/**
 * Daily task execution counts per owner.
 * @type {[taskName: string, counts: { [ownerId: number]: number }][]}
 */
const DATA_TASK_DAILY = [
  ["Support", {1:7, 2:3, 3:1}],
];

/**
 * Timed task execution counts per owner.
 * @type {[taskName: string, dueDate: string, counts: { [ownerId: number]: number }][]}
 */
const DATA_TASK_TIMED = [
  ["Expansion Drill", "2026-06-02", {1:40, 2:58, 3:58}],
  ["Extreme Peak",    "2026-06-09", {1:0,  2:58, 3:98}],
];

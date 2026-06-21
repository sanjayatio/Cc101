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

/**
 * Resources per owner.
 * @type {[resource: string, counts: { [ownerId: number]: number }][]}
 */
const DATA_RESOURCES = [
  ["Tickets",         {1: 160, 2:  50, 3: 270}],
  ["Collapse Pieces", {1: 601, 2:1046, 3: 319}],
  ["Dorittos",        {1:1877, 2: 694, 3:4815}],
];

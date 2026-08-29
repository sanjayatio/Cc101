// Test data for task module — kept small and deterministic.

/**
 * Owner definitions.
 * @type {[ownerId: number, ownerTag: string, startDate: string][]}
 */
const DATA_OWNER = [
  [1, "GM", "2024-01-01"],
  [2, "IB", "2024-01-01"],
];

/**
 * Daily task execution counts per owner.
 * @type {[taskName: string, counts: { [ownerId: number]: number }][]}
 */
const DATA_TASK_DAILY = [
  ["Daily Login",   {1:5, 2:3}],
  ["Resource Run",  {1:2, 2:2}],
];

/**
 * Timed task execution counts per owner.
 * @type {[taskName: string, dueDate: string, counts: { [ownerId: number]: number }][]}
 */
const DATA_TASK_TIMED = [
  ["Event Quest A", "2025-12-31", {1:1, 2:0}],
];

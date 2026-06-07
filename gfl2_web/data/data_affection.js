/**
 * Per-owner affection levels for each doll.
 * Omitting an owner key means that owner doesn't have that doll.
 * @type {{ [doll: string]: { [owner: string]: number } }}
 */
const RAW_OWNERSHIP = {
  "Vepley":       { "GM": 0, "IB": 4, "FB": 0 },
  "Groza":        { "GM": 0, "IB": 1, "FB": 0 },
  "Colphne":      { "GM": 4, "IB": 0, "FB": 0 },
  "Nemesis":      { "GM": 0, "IB": 0, "FB": 0 },
  "Krolik":       { "GM": 0, "IB": 1, "FB": 3 },

  "Sakura":       { "GM": 0 },
  "Florence":     { "GM": 0,          "FB": 4 },
  "Lewis":        {          "IB": 1 },
  "Nikketa":      { "GM": 4, "IB": 0, "FB": 0 },
  "Peri":         { "GM": 0 },
  "Qiuhua":       {          "IB": 0, "FB": 0 },
  "Sabrina":      { "GM": 1, "IB": 0, "FB": 0 },
  "Peritya":      { "GM": 0, "IB": 4, "FB": 0 },
  "Helen":        {          "IB": 1 },

  "Springfield":  { "GM": 0, "IB": 4, "FB": 0 },
  "Makiatto":     { "GM": 0, "IB": 3, "FB": 0 },
  "Centaureissi": { "GM": 4,          "FB": 4 },
  "Sharkry":      { "GM": 0, "IB": 0, "FB": 0 },

  "Lind":         { "GM": 0, "IB": 4, "FB": 0 },
  "Qiongjiu":     { "GM": 4, "IB": 3, "FB": 0 },
  "Tololo":       { "GM": 0, "IB": 0, "FB": 4 },
  "Cheeta":       { "GM": 0, "IB": 0, "FB": 0 },

  "Papasha":      { "GM": 4, "IB": 1, "FB": 0 },
  "Mosin-Nagant": { "GM": 0, "IB": 4, "FB": 0 },
  "Ksenia":       { "GM": 0, "IB": 0, "FB": 0 },
  "Nagant":       { "GM": 0, "IB": 0, "FB": 0 },

  "Balthilde":    { "GM": 0, "IB": 0, "FB": 0 },
  "Suomi":        {          "IB": 0, "FB": 4 },
  "Ullrid":       {          "IB": 0, "FB": 3 },
  "Dushevnaya":   {          "IB": 4 },
  "Lotta":        { "GM": 0, "IB": 0, "FB": 0 },
  "Littara":      { "GM": 4, "IB": 0, "FB": 0 },

  "Zhaohui":      { "GM": 4,          "FB": 0 },
  "Faye":         { "GM": 0, "IB": 3, "FB": 0 },
  "Jiangyu":      { "GM": 1,          "FB": 4 },
  "Daiyan":       { "GM": 0,          "FB": 0 },

  "Lenna":        { "GM": 4 },
  "Leva":         {                   "FB": 4 },

  "Klukai":       { "GM": 0, "IB": 4, "FB": 1 },
  "Mechty":       { "GM": 1, "IB": 1, "FB": 4 },
  "Andoris":      { "GM": 4, "IB": 0, "FB": 0 },
  "Belka":        {                   "FB": 0 },

  "Vector":       { "GM": 4, "IB": 4, "FB": 4 },

  "Yoohee":       { "GM": 4, "IB": 4 },

  "Robella":      { "GM": 4 },

  "Alva":         { "GM": 1 },
  "Voymastina":   {                   "FB": 1 },
};

export const formatNumber = (number, decimals = 2) => {
    if (number === undefined || number === null) return "0";
    return Math.round(number * Math.pow(10, decimals)) / Math.pow(10, decimals);
  };
import type { FilterDef } from "../lib/transform";

interface FilterSelectProps {
  filter: FilterDef;
  value: string[];
  onChange: (value: string[]) => void;
}

export function FilterSelect({ filter, value, onChange }: FilterSelectProps) {
  return (
    <label>
      {filter.label}
      <select
        multiple
        value={value}
        onChange={(event) =>
          onChange([...event.target.selectedOptions].map((option) => option.value))
        }
      >
        {filter.options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

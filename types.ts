export interface Group {
  id: string;
  name: string;
  parentId: string | null;
  subGroups?: Group[];
}

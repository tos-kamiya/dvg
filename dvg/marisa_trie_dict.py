try:
    import marisa
except:
    AVAILABLE = False
else:
    AVAILABLE = True

    from typing import Iterable, List, Tuple

    class Dict:
        def __init__(self, keys: Iterable[str]):
            self.keyset = marisa.Keyset()
            key_appeared_set = set()
            for key in keys:
                if key in key_appeared_set:
                    raise KeyError("KeyError: duplicated key: %s" % repr(key))
                self.keyset.push_back(key)
            self.trie = marisa.Trie()
            self.trie.build(self.keyset)
        
        def __getitem__(self, key: str) -> int:
            agent = marisa.Agent()
            agent.set_query(key)
            if not self.trie.lookup(agent):
                raise KeyError("KeyError: %s" % repr(key))
            return agent.key_id()
        
        def get(self, key: str, value_when_missing: int = -1) -> int:
            agent = marisa.Agent()
            agent.set_query(key)
            if not self.trie.lookup(agent):
                return value_when_missing
            return agent.key_id()

        def keys(self) -> List[int]:
            count = self.trie.num_keys()
            agent =  marisa.Agent()
            key_list = []
            for i in range(count):
                agent.set_query(i)
                r = self.trie.reverse_lookup(agent)
                assert r
                key_list.append(agent.key_str())
            return key_list
        
        def items(self) -> List[Tuple[str, int]]:
            count = self.trie.num_keys()
            agent =  marisa.Agent()
            item_list = []
            for i in range(count):
                agent.set_query(i)
                r = self.trie.reverse_lookup(agent)
                assert r
                item_list.append((agent.key_str(), i))
            return item_list
        
        def values(self) -> List[int]:
            count = self.trie.num_keys()
            return list(range(count))
        
        def __len__(self) -> int:
            return self.trie.num_keys()

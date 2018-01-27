def build_bom(results):
    """
    build the bill of material from the results for a given component
    """
    final_result = []
    root_product = list(results[0].keys())[0]
    batch_size = 1000
    required_quantity_dict = {root_product: batch_size}
    for index, component in enumerate(results):
        level = results[index]['level']
        print(component)
        for name, sub_component in results[index].items():
            if name not in  ['required_quantity', 'level']:
                sub_base = components_data[['Quantité de base Nomenclature', 'Unité de mesure pour Qté de base opérati']].loc[components_data.components == name].values[0]
                sub_base_quantity = float(sub_base[0])
                print('level', component['level'], 'sub_item', name , 'quantité de base ', sub_base_quantity, sub_base[1])
                sub_required_quantity = required_quantity_dict.get(name, sub_base_quantity)
                unit = components_data.loc[components_data.sub_components == name]['Unité de mesure du composant'].values[0]
                print('sub_item', name , 'quantité requise ', sub_required_quantity, unit)
                for item, quantity in sub_component.items():
                    element_dict = {}
                    infos = components_data[['Unité de mesure du composant', 'Description composant nomenclature', 'Fixé']]
                    infos = infos.loc[operator.and_(components_data.sub_components == item, components_data.components == name)].values[0]
                    sub_unit = infos[0]
                    sub_name = infos[1]
                    fixed = infos[2]
                    if sub_unit in ['PCY', '/PC']:
                        if not fixed :
                            new_quantity = np.ceil((np.ceil(quantity )* sub_required_quantity) / sub_base_quantity)
                        else :
                            new_quantity = np.ceil(quantity)
                    else:
                        if not fixed:
                            new_quantity = (quantity * sub_required_quantity) / sub_base_quantity
                        else:
                            new_quantity = quantity
                    print ('required quantity of ', item, ' = ', new_quantity, sub_unit)
                    results[index][name][item] = new_quantity
                    element_dict['item'] = item
                    element_dict['level'] = level
                    element_dict['quantity'] = new_quantity
                    element_dict['unit'] = sub_unit
                    element_dict['name'] = sub_name
                    if item not in base_material.values:
                        required_quantity_dict[item] = new_quantity
                    final_result.append(element_dict)
        results[index]['required_quantity'] = sub_required_quantity
    return pd.DataFrame(final_result)

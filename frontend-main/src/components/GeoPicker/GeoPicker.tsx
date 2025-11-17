import { type ChangeEvent, type FC, Fragment, useMemo, useState } from 'react';
import {
    ActionIcon,
    Flex,
    Loader,
    Stack,
    Text,
    Autocomplete,
    Button,
    type ButtonProps,
    type OptionsFilter,
} from '@mantine/core';
import { MapPinnedIcon } from 'lucide-react';
import { useDebouncedValue, useDisclosure } from '@mantine/hooks';
import { type Place, usePlaces } from '@/api/places';
import { MapEditor } from '@/components/MapEditor';

type GeoPickerOnChange = (value: Place | null) => void

export type GeoPickerProps = {
    value?: Place;
    defaultPlace?: Place | null;
    onChange?: GeoPickerOnChange;
    withAsterisk?: boolean;
    label?: string;
    placeholder?: string;
    error?: string;
    disabled?: boolean;
    description?: string;
    onlyButton?: boolean;
    buttonProps?: ButtonProps
}

const noFilter: OptionsFilter = ({ options }) => options;

export const GeoPicker: FC<GeoPickerProps> = ({ onChange, value, onlyButton, buttonProps, defaultPlace, ...props }) => {
    const initialPoint = useMemo<Place | null>(() => {
        if (!value) return null;
        return value;
    }, [value]);

    const [opened, { open, close }] = useDisclosure(false);

    const [search, setSearch] = useState(initialPoint?.address || '');
    const [selected, setSelected] = useState<Place | null>(initialPoint);
    const [debouncedSearch] = useDebouncedValue(selected ? '' : search, 300);

    const { data, isFetching } = usePlaces({ query: debouncedSearch.trim() });

    const handleInput = (e: ChangeEvent<HTMLInputElement>) => {
        setSearch(e.currentTarget.value);
        setSelected(null);
    };

    const handleChange = (place: Place) => {
        setSearch(place.address);
        setSelected(place);
        onChange?.(place);
    };

    const handleSelect = (placeId: string) => {
        const foundPlace = data?.find((item) => item.id === placeId);
        if (!foundPlace) return;

        handleChange(foundPlace);
    };

    const handleConfirmDrawer = (place: Place) => {
        handleChange(place);
        close();
    };

    if (onlyButton) {
        return (
            <Fragment>
                <Button
                    disabled={props.disabled}
                    onClick={open}
                    leftSection={<MapPinnedIcon size={18} />}
                    size="xs"
                    {...buttonProps}
                >Изменить место</Button>

                <MapEditor
                    opened={opened}
                    onClose={close}
                    value={selected}
                    defaultPlace={defaultPlace}
                    onConfirm={handleConfirmDrawer}
                />
            </Fragment>
        );
    }

    return (
        <Flex gap="xs" align="end" w="100%">
            <Autocomplete
                value={search}
                onInput={handleInput}
                data={data?.map(({ id, name }) => ({ value: id, label: name }))}
                onOptionSubmit={handleSelect}
                renderOption={({ option }) => {
                    const renderItem = data?.find(({ id }) => id === option.value);
                    if (!renderItem) return;
                    return (
                        <Stack gap={0}>
                            {renderItem.name}
                            <Text size="xs" c="dimmed" truncate="end">{renderItem.address}</Text>
                        </Stack>
                    );
                }}
                rightSection={isFetching ? <Loader size="xs" /> : (
                    <ActionIcon
                        disabled={props.disabled}
                        size={32}
                        variant="transparent"
                        color="dark"
                        onClick={open}
                    >
                        <MapPinnedIcon />
                    </ActionIcon>
                )}
                filter={noFilter}
                w="100%"
                {...props}
            />

            <MapEditor
                opened={opened}
                onClose={close}
                value={selected}
                defaultPlace={defaultPlace}
                onConfirm={handleConfirmDrawer}
            />
        </Flex>
    );
};
